from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime(timezone=True), index=True)
    provider = Column(String)
    raw_response = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PricePoint(Base):
    __tablename__ = "price_points"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime(timezone=True), index=True)
    provider = Column(String)


class MovingAverage(Base):
    __tablename__ = "moving_averages"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    average = Column(Float)
    computed_at = Column(DateTime, server_default=func.now())


class PollingJob(Base):
    __tablename__ = "polling_jobs"

    id = Column(String, primary_key=True)
    symbols = Column(JSON)
    interval = Column(Integer)
    provider = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())