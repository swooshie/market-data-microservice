from __future__ import annotations

import asyncio, json, logging, os
from datetime import datetime, timezone
from confluent_kafka import Consumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.market import MovingAverage, PricePoint

logging.basicConfig(level=logging.INFO)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = "price-events"

consumer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "ma-consumer-group",
    "auto.offset.reset": "earliest",
}



async def upsert_moving_average(session: AsyncSession, symbol: str, avg: float) -> None:
    stmt = select(MovingAverage).where(MovingAverage.symbol == symbol)
    result = await session.execute(stmt)
    ma = result.scalar_one_or_none()

    if ma:
        ma.average = avg
        ma.computed_at = datetime.now(timezone.utc)
    else:
        ma = MovingAverage(symbol=symbol, average=avg)
        session.add(ma)

    await session.flush()


async def get_last_prices(session: AsyncSession, symbol: str, limit: int = 5) -> list[float]:
    rows = await session.execute(
        select(PricePoint.price)
        .where(PricePoint.symbol == symbol)
        .order_by(PricePoint.timestamp.desc())
        .limit(limit)
    )
    return [row[0] for row in rows.fetchall()][::-1]   # oldest→newest


def calculate_moving_average(prices: list[float]) -> float:
    return round(sum(prices) / len(prices), 2)


async def process_message(payload: dict, session: AsyncSession) -> None:
    symbol = payload["symbol"].upper()
    price = float(payload["price"])
    ts = datetime.fromisoformat(payload["timestamp"])

    session.add(
        PricePoint(
            symbol=symbol,
            price=price,
            timestamp=ts,
            provider=payload.get("provider"),
        )
    )
    await session.flush()
    prices = await get_last_prices(session, symbol)
    if len(prices) < 5:                       # not enough data yet
        logging.info("Waiting for 5 points for %s (%d/5)", symbol, len(prices))
        await session.commit()
        return

    avg = calculate_moving_average(prices)
    await upsert_moving_average(session, symbol, avg)

    await session.commit()                    # ② single commit
    logging.info("5-pt MA updated → %s : %s", symbol, avg)


async def consume() -> None:
    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC])
    logging.info("Consumer connected to %s, topic=%s", KAFKA_BOOTSTRAP_SERVERS, TOPIC)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            if msg.error():
                logging.error("Kafka error: %s", msg.error())
                continue

            try:
                payload = json.loads(msg.value())
            except json.JSONDecodeError as e:
                logging.error("Bad JSON: %s", e)
                continue

            async with async_session() as session:
                await process_message(payload, session)

    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Consumer shutdown")
    finally:
        consumer.close()