import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.core.database import engine
from app.models.base import Base
from app.models import market

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Optional: for dev
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init())