from contextlib import asynccontextmanager
from app.models import user, shorturl
from app.db.session import Base, engine
from app.api.api import api_router
from app.services.geoip import init_geoip, close_geoip
from fastapi import FastAPI


@asynccontextmanager
async def create_tables(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        init_geoip()
        yield
    finally:
        close_geoip()


app = FastAPI(title="URL Shortener + Analytics", lifespan=create_tables)

app.include_router(api_router)
