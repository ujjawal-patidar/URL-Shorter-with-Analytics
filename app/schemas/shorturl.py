from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ShortURlCreate(BaseModel):
    original_url: str


class ShortURLResponse(BaseModel):
    original_url: str
    short_code: str
    is_active: bool
    click_count: int
    created_at: datetime

    class Config:
        # this made pydantic access values via attributes not as a key of dict as we are passing sqlalchemy obj
        from_attributes = True
