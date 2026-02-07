from app.models import user, shorturl
from app.db.session import Base, engine
from app.api.api import api_router
from fastapi import FastAPI


app = FastAPI(title="URL Shortener + Analytics")


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup() -> None:
    await create_tables()


app.include_router(api_router)


@app.get("/health")
def health_check() -> dict:
    return {"response": "ok"}


# @app.get("/")
# def db_check(db : AsyncSession = Depends(get_db)):
#     print("hello")
