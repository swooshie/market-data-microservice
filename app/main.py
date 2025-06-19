import uvicorn
from fastapi import FastAPI

from app.core.cache import redis
from app.core.kafka import get_kafka_producer
from app.core.limiter import add_rate_limiting

from .api.routes import router as api_router
from .core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)
add_rate_limiting(app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

import asyncio

from app.services import moving_average_consumer


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(moving_average_consumer.consume())


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()  # if redis client supports async close
    producer = get_kafka_producer()
    producer.flush()  # synchronous, no await
