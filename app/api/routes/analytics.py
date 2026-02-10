from datetime import date, datetime, time
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analytics import Analytics
from app.models.shorturl import ShortURL
from app.schemas.analytics import AnalyticsResponse
from app.db.session import get_async_db
from app.schemas.analytics import OrderEnum

router = APIRouter()


@router.get("/{short_code}", response_model=List[AnalyticsResponse])
async def get_analytics(
    short_code: str,
    start_date: date | None = None,
    end_date: date | None = None,
    order: Annotated[OrderEnum, Query(description="Sort order")] = OrderEnum.desc,
    db: AsyncSession = Depends(get_async_db),
):
    # Fetch the short URL
    result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
    short_url = result.scalar_one_or_none()
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # default start_date id id the short URL creation date
    if not start_date:
        start_date = short_url.created_at.date()

    # taking analytics
    query = select(Analytics).where(
        Analytics.short_code_id == short_url.id, Analytics.clicked_at >= start_date
    )

    if end_date:
        end_of_day = datetime.combine(end_date, time.max)
        query = query.where(Analytics.clicked_at <= end_of_day)

    if order == OrderEnum.asc:
        query = query.order_by(Analytics.clicked_at.asc())
    else:
        query = query.order_by(Analytics.clicked_at.desc())

    result = await db.execute(query)
    analytics_list = result.scalars().all()

    return [
        AnalyticsResponse(
            clicked_at=a.clicked_at,
            ip_address=a.ip_address,
            country=a.country,
            city=a.city,
            browser=a.browser,
            os=a.os,
            device_type=a.device_type,
            referrer=a.referrer,
        )
        for a in analytics_list
    ]
