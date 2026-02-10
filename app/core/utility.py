import string, random
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from app.models.shorturl import ShortURL
from app.models.daily_stats import DailyURLStats

from fastapi import Request
from user_agents import parse

from app.db.session import AsyncSessionLocal
from app.models.analytics import Analytics
from app.services.geoip import get_geo_info_from_ip
from user_agents import parse
from upstash_redis.asyncio import Redis

redis = Redis.from_env()

# a - z // A - Z // 0 - 9
ALPHABET = string.ascii_letters + string.digits

# length of the short code
CODE_LENGTH = 8


async def generate_unique_short_code(db: AsyncSession, length: int = CODE_LENGTH) -> str:
    for _ in range(10):
        short_code = "".join(random.choices(ALPHABET, k=length))

        # now if short_code already exists retry max 10 times
        result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
        existing = result.scalar_one_or_none()
        if not existing:
            return short_code
    raise Exception("failed to generate unique short code after max 10 attempts")


async def get_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        if request and request.client:
            client_ip = request.client.host

    if not client_ip or client_ip == "127.0.0.1":
        return "14.0.0.0"  # just for avoiding demo
    return client_ip


# async def save_analytics(
#     request,
#     short_url_id,
#     user_agent: str | None,
# ):
#     async with AsyncSessionLocal() as db:
#         ip = await get_ip(request)
#         user = parse(user_agent) if user_agent else None

#         geo = None
#         try:
#             geo = get_geo_info_from_ip(ip)
#         except Exception:
#             print("No data related to IP")

#         analytics = Analytics(
#             short_code_id=short_url_id,
#             ip_address=ip,
#             referrer=request.headers.get("referer"),
#             browser=user.browser.family if user else None,
#             os=user.os.family if user else None,
#             device_type=user.device.family if user else None,
#             country=geo.country.name if geo and geo.country else None,
#             city=geo.city.name if geo and geo.city else None,
#             latitude=geo.location.latitude if geo and geo.location else None,
#             longitude=geo.location.longitude if geo and geo.location else None,
#         )

#         db.add(analytics)
#         await db.commit()

#         # Now will Updating the daily stats
#         today = date.today()

#         # taking todays stats from DailyStates
#         result = await db.execute(
#             select(DailyURLStats).where(
#                 DailyURLStats.short_url_id == short_url_id, DailyURLStats.date_of_stat == today
#             )
#         )
#         daily_stats = result.scalar_one_or_none()

#         if not daily_stats:
#             # Will Create a new row if it is not exist
#             daily_stats = DailyURLStats(
#                 short_url_id=short_url_id,
#                 date_of_stat=today,
#                 clicks=1,
#                 unique_visitors=1 if ip else 0,
#             )
#             db.add(daily_stats)
#         else:
#             # if not we will update oin the existing row
#             daily_stats.clicks += 1

#             if ip:
#                 already_clicked_today = await db.execute(
#                     select(Analytics.id)
#                     .where(
#                         Analytics.short_code_id == short_url_id,
#                         Analytics.ip_address == ip,
#                         func.date(Analytics.clicked_at) == today,
#                     )
#                     .limit(1)  # just need one row
#                 )
#                 if already_clicked_today.scalar() is None:
#                     daily_stats.unique_visitors += 1

#         await db.commit()


async def save_analytics(request: Request, short_url_id, user_agent: str | None):
    async with AsyncSessionLocal() as db:
        ip = await get_ip(request)
        user = parse(user_agent) if user_agent else None

        geo = None
        try:
            geo = get_geo_info_from_ip(ip)
        except Exception:
            print("No geo data for IP")

        today = date.today()

        # check if this IP already clicked today
        already_clicked_today = False
        if ip:
            result = await db.execute(
                select(Analytics.id)
                .where(
                    Analytics.short_code_id == short_url_id,
                    Analytics.ip_address == ip,
                    func.date(Analytics.clicked_at) == today,
                )
                .limit(1)
            )
            already_clicked_today = True if result.scalar() else False

        # get or create daily stats
        result = await db.execute(
            select(DailyURLStats).where(
                DailyURLStats.short_url_id == short_url_id, DailyURLStats.date_of_stat == today
            )
        )
        daily_stats = result.scalar_one_or_none()

        if not daily_stats:
            daily_stats = DailyURLStats(
                short_url_id=short_url_id,
                date_of_stat=today,
                clicks=1,
                unique_visitors=1,
            )
            db.add(daily_stats)
        else:
            daily_stats.clicks += 1
            if not already_clicked_today:
                daily_stats.unique_visitors += 1

        # Add analytics record AFTER updating daily stats
        analytics = Analytics(
            short_code_id=short_url_id,
            ip_address=ip,
            referrer=request.headers.get("referer"),
            browser=user.browser.family if user else None,
            os=user.os.family if user else None,
            device_type=user.device.family if user else None,
            country=geo.country.name if geo and geo.country else None,
            city=geo.city.name if geo and geo.city else None,
            latitude=geo.location.latitude if geo and geo.location else None,
            longitude=geo.location.longitude if geo and geo.location else None,
        )
        db.add(analytics)

        await db.commit()
