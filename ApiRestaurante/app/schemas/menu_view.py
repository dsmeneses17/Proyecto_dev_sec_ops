"""Pydantic schemas for menu-view analytics (RF22)."""

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
    ip_address: Optional[str] = None
    viewed_at: datetime

    class Config:
        from_attributes = True


class MenuViewDailyStat(BaseModel):
    """One data-point: views on a given date."""
    date: str  # YYYY-MM-DD
    views: int


class MenuViewStats(BaseModel):
    """Aggregated analytics returned to the restaurant admin."""
    restaurant_id: str
    slug: str
    total_views: int
    views_today: int
    views_last_7_days: int
    views_last_30_days: int
    daily_breakdown: list[MenuViewDailyStat] = []
