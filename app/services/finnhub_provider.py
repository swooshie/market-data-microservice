from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
import asyncio
import finnhub

from .provider import MarketDataProvider


class FinnhubProvider(MarketDataProvider):
    """
    Minimal async wrapper around finnhub-python.

    * `get_latest_price(symbol)`  →  (last_price, utc_timestamp)
    * `bulk_poll(symbols, interval)` → returns a dummy job-id for now
    """

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("FINNHUB_API_KEY", "d1a6alhr01qltimvfhq0d1a6alhr01qltimvfhqg")
        if not key:
            raise RuntimeError(
                "Finnhub API key missing. "
                "Set FINNHUB_API_KEY env variable or pass it explicitly."
            )

        # blocking SDK client
        self._client = finnhub.Client(api_key=key)

    # ---------- helpers ---------- #

    async def _quote(self, symbol: str) -> dict:
        """
        Call finnhub's /quote endpoint in a background thread.
        Returns dict: {"c": current price, "t": epoch_secs, ...}
        """
        return await asyncio.to_thread(self._client.quote, symbol.upper())

    # ---------- MarketDataProvider API ---------- #

    async def get_latest_price(self, symbol: str) -> tuple[float, datetime]:
        quote = await self._quote(symbol)
        price = float(quote["c"])
        ts = datetime.fromtimestamp(int(quote["t"]), tz=timezone.utc)
        return price, ts, quote

    async def bulk_poll(self, symbols: list[str], interval: int) -> str:
        """
        For now, just return a unique job-id so the endpoint responds.
        """
        return f"poll_{uuid.uuid4().hex[:6]}"