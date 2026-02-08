from app.db.session import Base
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, BigInteger, TIMESTAMP
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_url = Column(Text, nullable=False)
    short_code = Column(String, unique=True, nullable=False, index=True)

    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    click_count = Column(BigInteger, default=0)

    # created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # user = relationship("User" , back_populates="short_url")
