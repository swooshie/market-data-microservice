import pytest


@pytest.mark.asyncio
async def test_get_latest_price(client):
    r = await client.get("/prices/latest?symbol=AAPL")
    assert r.status_code == 200
    js = r.json()
    assert js["symbol"] == "AAPL"
    assert "price" in js and "timestamp" in js
