import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(base_url=BASE_URL) as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_latest_price(client):
    response = await client.get("/prices/latest?symbol=AAPL")
    assert response.status_code == 200
