from sqlalchemy import Column, ForeignKey, String, DateTime, Float
from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_code_id = Column(UUID(as_uuid=True), ForeignKey("short_urls.id"), nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

    country = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    device_type = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)

    referrer = Column(String(2000), nullable=True)
    ip_address = Column(String(50), nullable=True)

    short_url = relationship("ShortURL", back_populates="analytics")
