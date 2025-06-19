from datetime import datetime, timezone
import uuid
from ..services.provider import MarketDataProvider

class AlphaVantageProvider(MarketDataProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or "demo"  # fallback to Alpha Vantage demo key

    async def get_latest_price(self, symbol: str) -> tuple[float, datetime]:
        # TEMP: return dummy data
        return 150.25, datetime.now(timezone.utc)

    async def bulk_poll(self, symbols: list[str], interval: int) -> str:
        # TEMP: return dummy job ID
        return f"poll_{uuid.uuid4().hex[:6]}"