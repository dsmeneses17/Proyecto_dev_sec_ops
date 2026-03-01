"""Pydantic schemas for menu-view analytics (RF22 / CU-08)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MenuViewCreate(BaseModel):
    """Payload sent by the frontend when a public menu page is loaded."""
    slug: str = Field(..., max_length=120)
    source: str = Field("menu", max_length=20, pattern=r"^(menu|qr|direct)$")


class MenuViewOut(BaseModel):
    id: UUID
    restaurant_id: UUID
    slug: str
    source: str
    user_agent: Optional[str] = None
    ip_hash: Optional[str] = None
    referrer: Optional[str] = None
    viewed_at: datetime

    class Config:
        from_attributes = True


class MenuViewDailyStat(BaseModel):
    """One data-point: views on a given date."""
    date: str  # YYYY-MM-DD
    views: int


class MenuViewHourlyStat(BaseModel):
    """Views grouped by hour of the day (0-23)."""
    hour: int
    views: int


class DeviceStat(BaseModel):
    """Aggregated device / browser breakdown."""
    name: str
    count: int
    percentage: float


class MenuViewStats(BaseModel):
    """Aggregated analytics returned to the restaurant admin."""
    restaurant_id: str
    slug: str
    total_views: int
    views_today: int
    views_last_7_days: int
    views_last_30_days: int
    daily_breakdown: list[MenuViewDailyStat] = []
    # CU-08 – hourly distribution
    hourly_breakdown: list[MenuViewHourlyStat] = []
    # CU-08 – device / browser distribution
    device_breakdown: list[DeviceStat] = []
    browser_breakdown: list[DeviceStat] = []
    # RF24 – date-range metadata (only present when a custom range is used)
    start_date: Optional[str] = None   # YYYY-MM-DD
    end_date: Optional[str] = None     # YYYY-MM-DD
    filtered_views: Optional[int] = None
