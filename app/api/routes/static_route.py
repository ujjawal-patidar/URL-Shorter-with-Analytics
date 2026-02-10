from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"response": "ok"}


@router.get("/")
def db_Application_check(db: AsyncSession = Depends(get_async_db)):
    return {
        "Application": "URL Shortener + Analytics",
        "Application status": "running",
        "Postgres Database": "connected",
    }
