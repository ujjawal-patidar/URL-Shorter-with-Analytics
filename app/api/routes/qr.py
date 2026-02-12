from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import qrcode
import io
import base64
from app.models.shorturl import ShortURL
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.api.deps import get_current_user
from sqlalchemy import select
from app.core.utility import redis
from app.core.click_rate_limit import create_rate_limiter

router = APIRouter()


@router.get("/{short_code}")
@create_rate_limiter(max_creation=2, window=60)
async def get_qr(
    short_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):

    result = await db.execute(
        select(ShortURL).where(
            ShortURL.short_code == short_code, ShortURL.user_id == current_user.id
        )
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Short code not found")

    cache_key = f"qr:{short_code}"

    cached = await redis.get(cache_key)
    if cached:
        image_bytes = base64.b64decode(cached)
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    short_url = f"http://localhost:8000/{short_code}"
    qr = qrcode.make(short_url)

    buffer = io.BytesIO()
    qr.save(buffer, "png")

    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()

    await redis.set(cache_key, image_base64, ex=604800)

    buffer.seek(0)
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
