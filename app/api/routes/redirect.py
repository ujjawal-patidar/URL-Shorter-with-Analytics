from fastapi import APIRouter, Depends, Header, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.shorturl import ShortURL
from sqlalchemy import select, update
from app.core.utility import save_analytics
from app.core.utility import redis
from app.core.click_rate_limit import click_rate_limiter
import json

CACHE_EXPIRATION_TIME = 60 * 10

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to the original URL",
    response_description="Redirects the user to the original URL",
)
@click_rate_limiter(max_clicks=5, window=120)
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    user_agent: Annotated[str | None, Header()] = None,
):
    cache_key = f"short_code:{short_code}"

    cache_data = await redis.get(cache_key)

    if cache_data:
        data = json.loads(cache_data)

        background_tasks.add_task(
            save_analytics,
            request=request,
            short_url_id=data["short_url_id"],
            user_agent=user_agent,
        )

        print("cached")
        return RedirectResponse(url=data["original_url"], status_code=302)

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

    # cache DB result
    await redis.set(
        cache_key,
        json.dumps(
            {
                "short_url_id": str(short_url.id),
                "original_url": short_url.original_url,
            }
        ),
        ex=CACHE_EXPIRATION_TIME,
    )

    return RedirectResponse(url=short_url.original_url, status_code=302)
