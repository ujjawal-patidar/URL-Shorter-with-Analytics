from app.db.session import Base
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, BigInteger
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column


class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code = Column(String, unique=True, nullable=False, index=True)

    is_active = Column(Boolean, default=True)
    click_count = Column(BigInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # user = relationship("User" , back_populates="short_url")
    analytics = relationship("Analytics", back_populates="short_url", cascade="all, delete-orphan")
