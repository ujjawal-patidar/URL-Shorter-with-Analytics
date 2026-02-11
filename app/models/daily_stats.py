from datetime import date
from app.db.session import Base
from sqlalchemy import Column, Date, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID


class DailyURLStats(Base):
    __tablename__ = "daily_short_url_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    short_url_id = Column(
        UUID(as_uuid=True),
        ForeignKey("short_urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date_of_stat: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    clicks: Mapped[int] = mapped_column(BigInteger, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
