"""Analytics router – records and retrieves menu-view stats (RF22)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func as sa_func, cast, Date
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.restaurant import Restaurant
from app.models.menu_view import MenuView
from app.schemas.menu_view import MenuViewCreate, MenuViewOut, MenuViewStats, MenuViewDailyStat
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# ------------------------------------------------------------------ #
# PUBLIC – record a view (called by the frontend on every page load)
# ------------------------------------------------------------------ #
@router.post("/views", response_model=MenuViewOut, status_code=201)
def record_menu_view(
    payload: MenuViewCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a single menu visualisation.

    This endpoint is intentionally **unauthenticated** so that any visitor
    (even anonymous users scanning a QR code) can be counted.
    """

    restaurant = db.query(Restaurant).filter(Restaurant.slug == payload.slug).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Extract lightweight metadata from the incoming request.
    user_agent = (request.headers.get("user-agent") or "")[:512]
    ip_address = request.headers.get("x-forwarded-for") or request.client.host if request.client else None

    view = MenuView(
        restaurant_id=restaurant.id,
        slug=payload.slug,
        source=payload.source,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(view)
    db.commit()
    db.refresh(view)
    return view


# ------------------------------------------------------------------ #
# ADMIN – get stats for the current user's restaurant
# ------------------------------------------------------------------ #
@router.get("/stats", response_model=MenuViewStats)
def get_menu_view_stats(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated view statistics for the admin's restaurant."""

    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today_start - timedelta(days=7)
    thirty_days_ago = today_start - timedelta(days=30)

    base_q = db.query(MenuView).filter(MenuView.restaurant_id == restaurant.id)

    total_views = base_q.count()
    views_today = base_q.filter(MenuView.viewed_at >= today_start).count()
    views_last_7 = base_q.filter(MenuView.viewed_at >= seven_days_ago).count()
    views_last_30 = base_q.filter(MenuView.viewed_at >= thirty_days_ago).count()

    # Daily breakdown for the last 30 days
    daily_rows = (
        db.query(
            cast(MenuView.viewed_at, Date).label("day"),
            sa_func.count().label("cnt"),
        )
        .filter(
            MenuView.restaurant_id == restaurant.id,
            MenuView.viewed_at >= thirty_days_ago,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    daily_breakdown = [
        MenuViewDailyStat(date=str(row.day), views=row.cnt) for row in daily_rows
    ]

    return MenuViewStats(
        restaurant_id=str(restaurant.id),
        slug=restaurant.slug,
        total_views=total_views,
        views_today=views_today,
        views_last_7_days=views_last_7,
        views_last_30_days=views_last_30,
        daily_breakdown=daily_breakdown,
    )


@router.get("/stats/{restaurant_id}", response_model=MenuViewStats)
def get_menu_view_stats_by_id(
    restaurant_id: UUID,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated view statistics for a specific restaurant (admin only)."""

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Only the restaurant owner can see the stats
    if restaurant.admin_id != user["id"] and user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today_start - timedelta(days=7)
    thirty_days_ago = today_start - timedelta(days=30)

    base_q = db.query(MenuView).filter(MenuView.restaurant_id == restaurant.id)

    total_views = base_q.count()
    views_today = base_q.filter(MenuView.viewed_at >= today_start).count()
    views_last_7 = base_q.filter(MenuView.viewed_at >= seven_days_ago).count()
    views_last_30 = base_q.filter(MenuView.viewed_at >= thirty_days_ago).count()

    daily_rows = (
        db.query(
            cast(MenuView.viewed_at, Date).label("day"),
            sa_func.count().label("cnt"),
        )
        .filter(
            MenuView.restaurant_id == restaurant.id,
            MenuView.viewed_at >= thirty_days_ago,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    daily_breakdown = [
        MenuViewDailyStat(date=str(row.day), views=row.cnt) for row in daily_rows
    ]

    return MenuViewStats(
        restaurant_id=str(restaurant.id),
        slug=restaurant.slug,
        total_views=total_views,
        views_today=views_today,
        views_last_7_days=views_last_7,
        views_last_30_days=views_last_30,
        daily_breakdown=daily_breakdown,
    )
