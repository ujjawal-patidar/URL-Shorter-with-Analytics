from fastapi import APIRouter
from app.api.routes import auth, links, qr, redirect, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

api_router.include_router(links.router, prefix="/links", tags=["Links"])

api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

api_router.include_router(qr.router, prefix="/qr", tags=["QR"])

api_router.include_router(redirect.router, tags=["Redirect"])
