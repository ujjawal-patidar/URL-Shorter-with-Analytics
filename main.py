from fastapi import FastAPI, Depends
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, engine, Base
from app.models import user
import asyncio

app = FastAPI()
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_tables() 

@app.get("/health")
def health_check():
    return {"response" : "ok"}


# @app.get("/")
# def db_check(db : AsyncSession = Depends(get_db)):
#     print("hello")
