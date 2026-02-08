from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ShortURlCreate(BaseModel):
    user_id: UUID
    original_url: str


class ShortURLResponse(BaseModel):
    original_url: str
    short_code: str
    is_active: bool
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True  # this made pydantic access values via attributes not as a key of dict as we are passing sqlalchemy obj
