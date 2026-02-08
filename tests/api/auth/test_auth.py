from fastapi.testclient import TestClient
import pytest


@pytest.mark.asyncio
async def test_me_unauthorized(client):
    res = await client.get("/auth/me")  # no token
    assert res.status_code == 401
    data = res.json()
    assert data["detail"] == "Not authenticated"
