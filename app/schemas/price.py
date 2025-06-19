# schemas/price.py
from datetime import datetime

from pydantic import BaseModel, Field


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    provider: str = Field(examples=["alpha_vantage"])
