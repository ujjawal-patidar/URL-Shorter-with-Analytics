from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.shorturl import ShortURlCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.core.utility import generate_unique_short_code
from app.models.shorturl import ShortURL
from app.models.user import User
from app.schemas.shorturl import ShortURLResponse
from app.api.deps import get_current_user
from sqlalchemy import select
from app.core.click_rate_limit import create_rate_limiter

router = APIRouter()


@router.post("/", status_code=201)
@create_rate_limiter(max_creation=5, window=60)
async def create_short_link(
    data: ShortURlCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ShortURL).where(
        ShortURL.user_id == current_user.id, ShortURL.original_url == data.original_url
    )
    result = await db.execute(query)
    existing_link = result.scalar_one_or_none()

    if existing_link:
        # Return existing short URL instead of creating a new one
        return {
            "is_active": existing_link.is_active,
            "original_url": existing_link.original_url,
            "short_code": existing_link.short_code,
            "created_at": existing_link.created_at,
            "message": "Short URL already exists",
        }

    # generate a unique short code
    short_code = await generate_unique_short_code(db)

    new_link = ShortURL(
        user_id=current_user.id, original_url=data.original_url, short_code=short_code
    )

    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return {
        "is_active": new_link.is_active,
        "original_url": new_link.original_url,
        "short_code": new_link.short_code,
        "created_at": new_link.created_at,
    }


@router.get("/", response_model=list[ShortURLResponse], status_code=status.HTTP_200_OK)
async def get_all_links(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ShortURL).where(ShortURL.user_id == current_user.id))
    links = result.scalars().all()
    return links


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    # fetching short url owned by current_user
    result = await db.execute(
        select(ShortURL).where(
            ShortURL.short_code == short_code,
            ShortURL.user_id == current_user.id,
        )
    )

    short_url = result.scalars().first()

    # not found or if not owned by the current user
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    await db.delete(short_url)
    await db.commit()

    return {"message": f"Short Code - {short_url. short_code} Deleted Successfully"}


@router.patch("/{short_code}", status_code=status.HTTP_200_OK)
async def activate_deactivate_short_url(
    short_code: str,
    is_active: bool = Query(..., description="activate or deactivate the short URL"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch the link owned by current_user
    result = await db.execute(
        select(ShortURL).where(
            ShortURL.short_code == short_code,
            ShortURL.user_id == current_user.id,
        )
    )

    short_url = result.scalars().first()

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    short_url.is_active = is_active
    await db.commit()
    await db.refresh(short_url)

    return {
        "short_code": short_url.short_code,
        "is_active": short_url.is_active,
    }
