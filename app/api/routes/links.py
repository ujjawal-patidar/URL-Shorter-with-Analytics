from fastapi import APIRouter, Depends
from app.schemas.shorturl import ShortURlCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.core.utility import generate_unique_short_code
from app.models.shorturl import ShortURL
from app.models.user import User
from app.schemas.shorturl import ShortURLResponse
from app.api.deps import get_current_user
from sqlalchemy import select

router = APIRouter()


@router.post("/")
async def create_short_link(
    data: ShortURlCreate,
    db: AsyncSession = Depends(get_async_db),
):

    # generate a unique short code
    short_code = await generate_unique_short_code(db)

    new_link = ShortURL(user_id=data.user_id, original_url=data.original_url, short_code=short_code)

    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return {
        "is_active": new_link.is_active,
        "original_url": new_link.original_url,
        "short_code": new_link.short_code,
        "created_at": new_link.created_at,
    }


@router.get("/", response_model=list[ShortURLResponse])
async def get_all_links(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ShortURL).where(ShortURL.user_id == current_user.id))
    links = result.scalars().all()
    return links
