from datetime import date, datetime, time
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analytics import Analytics
from app.models.shorturl import ShortURL
from app.models.daily_stats import DailyURLStats
from app.schemas.analytics import AnalyticsResponse, DailyStatsResponse
from app.db.session import get_async_db
from app.schemas.analytics import OrderEnum
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get(
    "/{short_code}",
    response_model=List[AnalyticsResponse],
    description="Get all analytics details of the shortcode",
)
async def get_analytics(
    short_code: str,
    start_date: date | None = None,
    end_date: date | None = None,
    order: Annotated[OrderEnum, Query(description="Sort order")] = OrderEnum.desc,
    current_user: User = Depends(get_current_user),
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


@router.get("/dailyStats/{short_code}", response_model=List[DailyStatsResponse])
async def get_analytics_of_date(
    short_code: str,
    start_date: date | None = None,
    end_date: date | None = None,
    order: Annotated[OrderEnum, Query(description="Sort order")] = OrderEnum.desc,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    # Fetch short URL
    result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
    short_url = result.scalar_one_or_none()
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Default start_date is the creation date of shortURL
    if not start_date:
        start_date = short_url.created_at.date()

    query = select(DailyURLStats).where(
        DailyURLStats.short_url_id == short_url.id, DailyURLStats.date_of_stat >= start_date
    )

    if end_date:
        query = query.where(DailyURLStats.date_of_stat <= end_date)

    # Apply ordering
    if order == OrderEnum.asc:
        query = query.order_by(DailyURLStats.date_of_stat.desc())
    else:
        query = query.order_by(DailyURLStats.date_of_stat.asc())

    result = await db.execute(query)
    stats_list = result.scalars().all()

    return [
        DailyStatsResponse(
            date_of_stat=s.date_of_stat, clicks=s.clicks, unique_visitors=s.unique_visitors
        )
        for s in stats_list
    ]


@router.get("/total_clicks/{short_code}")
async def short_url_total_clicks(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
    short_url = result.scalar_one_or_none()

    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {"short_code": short_code, "total_clicks": short_url.click_count}
