from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from enum import Enum


class AnalyticsResponse(BaseModel):
    clicked_at: datetime
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    device_type: Optional[str] = None
    referrer: Optional[str] = None


class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class DailyStatsResponse(BaseModel):
    date_of_stat: date
    clicks: int
    unique_visitors: int
