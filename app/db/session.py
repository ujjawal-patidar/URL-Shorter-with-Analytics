import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")

if DATABASE_URI is None:
    raise ValueError("DATABASE_URI is not set")

# Now we will create a engine instance
engine = create_async_engine(
    DATABASE_URI,
    echo=True,
    future=True,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
    },
)


# NOW I AM CREATING A declaritive_base meta instance
class Base(DeclarativeBase):
    pass


AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
