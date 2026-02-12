import uuid
import pytest
from fastapi import Depends
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.db.session import get_async_db
from app.models.user import User
from app.core.security import get_password_hash

# pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client():
    # its new previously we use app = app, now its depreceated
    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def db_session():
    async for session in get_async_db():
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession):
    email = f"test_user_{uuid.uuid4()}@test.com"
    user = User(
        name="Test User",
        email=email,
        hashed_password=get_password_hash("Password@123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {"id": user.id, "email": user.email, "password": "Password@123"}


@pytest.fixture
async def auth_token(client, test_user):
    res = await client.post(
        "/auth/login", json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
async def auth_client(client, auth_token):
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client
