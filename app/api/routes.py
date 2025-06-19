from fastapi import APIRouter, Depends, Query
from ..core.dependencies import get_provider
from ..services.provider import MarketDataProvider
from ..schemas.price import PriceResponse
from ..schemas.poll import PollRequest, PollAcceptedResponse

router = APIRouter()
from ..models.market import RawMarketData
from ..core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..core.kafka import publish_price_event

@router.get("/prices/latest", response_model=PriceResponse)
async def get_latest_price(
    symbol: str,
    provider: str | None = None,
    market: MarketDataProvider = Depends(get_provider),
    session: AsyncSession = Depends(get_session),
):
    price, ts = await market.get_latest_price(symbol)

    raw = RawMarketData(
        id=str(uuid.uuid4()),
        symbol=symbol.upper(),
        price=price,
        timestamp=ts,
        provider=provider or market.__class__.__name__,
        raw_response={"dummy": True},  # will be actual API response later
    )
    session.add(raw)
    await session.commit()

    # Publish event to Kafka after commit
    event = {
        "symbol": raw.symbol,
        "price": raw.price,
        "timestamp": raw.timestamp.isoformat(),
        "source": raw.provider,
        "raw_response_id": raw.id,
    }
    publish_price_event(event)

    return PriceResponse(
        symbol=symbol.upper(),
        price=price,
        timestamp=ts,
        provider=provider or market.__class__.__name__,
    )

@router.post(
    "/prices/poll",
    status_code=202,
    response_model=PollAcceptedResponse,
    summary="kick off background polling job"
)
async def poll_prices(
    req: PollRequest,
    market: MarketDataProvider = Depends(get_provider),
):
    job_id = await market.bulk_poll(req.symbols, req.interval)
    return PollAcceptedResponse(job_id=job_id, config=req)