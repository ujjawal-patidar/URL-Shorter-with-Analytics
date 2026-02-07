import app.models.user  # noqa: F401
from app.db.session import Base, engine

from fastapi import FastAPI


app = FastAPI()


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup() -> None:
    await create_tables()


@app.get("/health")
def health_check() -> dict:
    return {"response": "ok"}


# @app.get("/")
# def db_check(db : AsyncSession = Depends(get_db)):
#     print("hello")
