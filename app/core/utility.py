import string, random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.shorturl import ShortURL

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
