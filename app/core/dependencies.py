from fastapi import Depends, HTTPException, status
from ..services.provider import MarketDataProvider
from ..services.alpha_vantage import AlphaVantageProvider
from .config import settings

def get_provider() -> MarketDataProvider:
    if settings.provider == "alpha_vantage":
        return AlphaVantageProvider(api_key=settings.alpha_vantage_api_key)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail=f"provider '{settings.provider}' not supported yet")