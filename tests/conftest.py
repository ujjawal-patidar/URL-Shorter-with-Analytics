import uuid
import pytest
from fastapi import FastAPI
from app.main import app
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.db.session import get_async_db, Base
from app.models.user import User
from app.core.security import get_password_hash

# Use pytest-asyncio
pytestmark = pytest.mark.asyncio

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False, class_=AsyncSession)


# create/drop tables once per session
@pytest.fixture(scope="session")
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# provide a session for each test
@pytest.fixture
async def db_session(setup_db):
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # rollback after each test for isolation between each test


# Override FastAPI dependency to use test DB
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    async def _override_get_async_db():
        async with db_session as s:
            yield s

    app.dependency_overrides[get_async_db] = _override_get_async_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


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
        "/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
async def auth_client(client, auth_token):
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client
