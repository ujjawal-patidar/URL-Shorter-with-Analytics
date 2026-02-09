import string, random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.shorturl import ShortURL
from fastapi import Request
from user_agents import parse

from app.db.session import AsyncSessionLocal
from app.models.analytics import Analytics
from app.services.geoip import get_geo_info_from_ip
from user_agents import parse

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
#         request,
#         short_url_id,
#         user-agent:str | None,
#     ):
# user_agent_info = parse(user_agent)
# browser =  user_agent and (user_agent_info.browser)
# os_name = user_agent and (user_agent_info.get_os())

# device = user_agent_info.get_device()

# ip = await get_ip(request)

# try:
#     referer = request.headers.get("referer")
#     geo_info = get_country_from_ip(ip)
#     country = geo_info and geo_info.country and (geo_info.country.name)
#     city = geo_info and geo_info.city and (geo_info.city.name)
#     latitude = geo_info and geo_info.location and (geo_info.location.latitude)
#     longitude = geo_info and geo_info.location and (geo_info.location.longitude)

# except Exception as err:
#     print("No Data for this IP")

# else:
#     return {
#         "browser" : browser[0] if browser else None,
#         "os" : os_name,
#         "device" : device,
#         "ip" :ip ,
#         "referer": referer,
#         "country" : country,
#         "city" : city,
#         "latitude" : latitude,
#         "longitude": longitude,
#         "geo_info" : geo_info
#     }
# app/tasks/analytics.py


async def save_analytics(
    request,
    short_url_id,
    user_agent: str | None,
):
    async with AsyncSessionLocal() as db:
        ip = await get_ip(request)
        user = parse(user_agent) if user_agent else None

        geo = None
        try:
            geo = get_geo_info_from_ip(ip)
        except Exception:
            print("No data related to IP")

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
