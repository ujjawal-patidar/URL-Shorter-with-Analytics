from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, Float
from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_code_id = Column(UUID(as_uuid=True), ForeignKey("short_urls.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    country: Mapped[str] = mapped_column(String(50), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    device_type: Mapped[str] = mapped_column(String(50), nullable=True)
    os: Mapped[str] = mapped_column(String(50), nullable=True)
    browser: Mapped[str] = mapped_column(String(50), nullable=True)

    referrer: Mapped[str] = mapped_column(String(2000), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)

    short_url = relationship("ShortURL", back_populates="analytics")
