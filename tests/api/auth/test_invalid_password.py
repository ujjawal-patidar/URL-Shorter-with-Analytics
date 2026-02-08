import pytest


@pytest.mark.asyncio
async def test_login_invalid_password(client, test_user):
    res = await client.post(
        "/auth/login", json={"email": test_user["email"], "password": "wrongpassword"}
    )
    assert res.status_code == 401
