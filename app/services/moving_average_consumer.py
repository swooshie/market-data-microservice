import asyncio
import json
import logging
from confluent_kafka import Consumer, KafkaException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models.market import PricePoint, MovingAverage
from sqlalchemy import select, update
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "price-events"

consumer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "ma-consumer-group",
    "auto.offset.reset": "earliest",
}

async def upsert_moving_average(session: AsyncSession, symbol: str, avg: float):
    stmt = select(MovingAverage).where(MovingAverage.symbol == symbol)
    result = await session.execute(stmt)
    ma = result.scalar_one_or_none()
    if ma:
        ma.average = avg
        ma.computed_at = datetime.utcnow()
    else:
        ma = MovingAverage(symbol=symbol, average=avg)
        session.add(ma)
    await session.commit()

async def get_last_prices(session: AsyncSession, symbol: str, limit: int = 5):
    stmt = (
        select(PricePoint.price)
        .where(PricePoint.symbol == symbol)
        .order_by(PricePoint.timestamp.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    prices = [row[0] for row in result.fetchall()]
    return prices

def calculate_moving_average(prices: list[float]) -> float:
    if not prices:
        return 0
    return sum(prices) / len(prices)

async def process_message(msg, session: AsyncSession):
    try:
        data = json.loads(msg.value())
        symbol = data["symbol"]
        price = float(data["price"])
        timestamp = datetime.fromisoformat(data["timestamp"])

        # Save PricePoint
        pp = PricePoint(symbol=symbol, price=price, timestamp=timestamp, provider=data.get("source"))
        session.add(pp)
        await session.commit()

        # Compute MA
        prices = await get_last_prices(session, symbol)
        ma = calculate_moving_average(prices)

        # Upsert MA
        await upsert_moving_average(session, symbol, ma)
        logging.info(f"Updated MA for {symbol}: {ma}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")

async def consume():
    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC])
    logging.info("Kafka consumer started, listening to topic price-events")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            if msg.error():
                logging.error(f"Kafka error: {msg.error()}")
                continue

            async with async_session() as session:
                await process_message(msg, session)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()