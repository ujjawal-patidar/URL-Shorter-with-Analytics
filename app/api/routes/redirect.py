from fastapi import APIRouter, Depends, Header, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.shorturl import ShortURL
from sqlalchemy import select, update
from app.core.utility import save_analytics

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    user_agent: Annotated[str | None, Header()] = None,
):
    # print(user_agent)
    # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36
    result = await db.execute(
        select(ShortURL).where(ShortURL.short_code == short_code, ShortURL.is_active == True)
    )

    short_url = result.scalar_one_or_none()

    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    await db.execute(
        update(ShortURL)
        .where(ShortURL.id == short_url.id)
        .values(click_count=ShortURL.click_count + 1)
    )
    await db.commit()

    background_tasks.add_task(
        save_analytics, request=request, short_url_id=short_url.id, user_agent=user_agent
    )

    return RedirectResponse(url=short_url.original_url, status_code=302)
