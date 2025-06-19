import asyncio
import json
import os

from redis.asyncio import Redis  # note the redis.asyncio submodule

redis = Redis(host="localhost", port=6379, db=0)


async def get_cached_price(symbol: str):
    return await redis.get(symbol)


async def cache_price(symbol: str, payload: dict, ttl=30):
    await redis.set(symbol, json.dumps(payload), ex=ttl)
