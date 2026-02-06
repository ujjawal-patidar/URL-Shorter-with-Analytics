import os

from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker , AsyncSession
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()
load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")


# Now we will create a engine instance
engine = create_async_engine(DATABASE_URI, echo=True, future=True, pool_pre_ping=True,connect_args={"statement_cache_size": 0,})


#NOW I AM CREATING A declaritive_base meta instance
class Base(DeclarativeBase):
    pass

AsyncSessionLocal = async_sessionmaker( 
    bind = engine,
    class_= AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()