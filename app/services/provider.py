from abc import ABC, abstractmethod
from datetime import datetime

class MarketDataProvider(ABC):
    """contract every provider impl must satisfy"""

    @abstractmethod
    async def get_latest_price(self, symbol: str) -> tuple[float, datetime]:
        """return (price, utc_timestamp)"""

    @abstractmethod
    async def bulk_poll(
        self, symbols: list[str], interval: int
    ) -> str: 
        """kick off polling job and hand back opaque id"""