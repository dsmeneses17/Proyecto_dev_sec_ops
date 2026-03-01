"""Analytics router – records and retrieves menu-view stats (RF22 / RF24 / CU-08)."""

from __future__ import annotations

import csv
import io
import re
from datetime import date as date_type, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func as sa_func, cast, Date, extract
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.restaurant import Restaurant
from app.models.menu_view import MenuView, _hash_ip
from app.schemas.menu_view import (
    MenuViewCreate,
    MenuViewOut,
    MenuViewStats,
    MenuViewDailyStat,
    MenuViewHourlyStat,
    DeviceStat,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# ------------------------------------------------------------------ #
# Lightweight user-agent classifier
# ------------------------------------------------------------------ #
_MOBILE_RE = re.compile(r"Mobile|Android|iPhone|iPad|iPod|Opera Mini|IEMobile", re.I)
_BROWSER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Chrome",  re.compile(r"Chrome/[\d.]+")),
    ("Safari",  re.compile(r"Safari/[\d.]+(?!.*Chrome)")),
    ("Firefox", re.compile(r"Firefox/[\d.]+")),
    ("Edge",    re.compile(r"Edg/[\d.]+")),
    ("Opera",   re.compile(r"OPR/[\d.]+")),
]


def _classify_device(ua: str | None) -> str:
    if not ua:
        return "Desconocido"
    return "Móvil" if _MOBILE_RE.search(ua) else "Escritorio"


def _classify_browser(ua: str | None) -> str:
    if not ua:
        return "Desconocido"
    # Edge contains "Chrome" – test Edge first
    if re.search(r"Edg/", ua):
        return "Edge"
    for name, pat in _BROWSER_PATTERNS:
        if pat.search(ua):
            return name
    return "Otro"


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
    raw_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else None)
    referrer = (request.headers.get("referer") or None)

    view = MenuView(
        restaurant_id=restaurant.id,
        slug=payload.slug,
        source=payload.source,
        user_agent=user_agent,
        ip_hash=_hash_ip(raw_ip),
        referrer=referrer[:512] if referrer else None,
    )
    db.add(view)
    db.commit()
    db.refresh(view)
    return view


# ------------------------------------------------------------------ #
# HELPER – build stats for a given restaurant (avoids duplication)
# ------------------------------------------------------------------ #
def _build_stats(
    db: Session,
    restaurant: Restaurant,
    start_date: Optional[date_type] = None,
    end_date: Optional[date_type] = None,
) -> MenuViewStats:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today_start - timedelta(days=7)
    thirty_days_ago = today_start - timedelta(days=30)

    base_q = db.query(MenuView).filter(MenuView.restaurant_id == restaurant.id)

    total_views = base_q.count()
    views_today = base_q.filter(MenuView.viewed_at >= today_start).count()
    views_last_7 = base_q.filter(MenuView.viewed_at >= seven_days_ago).count()
    views_last_30 = base_q.filter(MenuView.viewed_at >= thirty_days_ago).count()

    # ---- date-range for the breakdowns (RF24) ----
    if start_date and end_date:
        range_start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        range_end = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
    else:
        range_start = thirty_days_ago
        range_end = now

    range_filter = [
        MenuView.restaurant_id == restaurant.id,
        MenuView.viewed_at >= range_start,
        MenuView.viewed_at <= range_end,
    ]

    # ---- daily breakdown ----
    daily_rows = (
        db.query(cast(MenuView.viewed_at, Date).label("day"), sa_func.count().label("cnt"))
        .filter(*range_filter)
        .group_by("day")
        .order_by("day")
        .all()
    )
    daily_breakdown = [MenuViewDailyStat(date=str(r.day), views=r.cnt) for r in daily_rows]

    # ---- CU-08: hourly distribution ----
    hourly_rows = (
        db.query(
            extract("hour", MenuView.viewed_at).label("hr"),
            sa_func.count().label("cnt"),
        )
        .filter(*range_filter)
        .group_by("hr")
        .order_by("hr")
        .all()
    )
    hourly_map = {int(r.hr): r.cnt for r in hourly_rows}
    hourly_breakdown = [MenuViewHourlyStat(hour=h, views=hourly_map.get(h, 0)) for h in range(24)]

    # ---- CU-08: device & browser distribution ----
    ua_rows = (
        db.query(MenuView.user_agent)
        .filter(*range_filter)
        .all()
    )
    device_counts: dict[str, int] = {}
    browser_counts: dict[str, int] = {}
    for (ua,) in ua_rows:
        d = _classify_device(ua)
        b = _classify_browser(ua)
        device_counts[d] = device_counts.get(d, 0) + 1
        browser_counts[b] = browser_counts.get(b, 0) + 1

    total_in_range = len(ua_rows) or 1  # avoid division by zero
    device_breakdown = sorted(
        [DeviceStat(name=k, count=v, percentage=round(v / total_in_range * 100, 1)) for k, v in device_counts.items()],
        key=lambda x: x.count, reverse=True,
    )
    browser_breakdown = sorted(
        [DeviceStat(name=k, count=v, percentage=round(v / total_in_range * 100, 1)) for k, v in browser_counts.items()],
        key=lambda x: x.count, reverse=True,
    )

    filtered_views = sum(d.views for d in daily_breakdown) if (start_date and end_date) else None

    return MenuViewStats(
        restaurant_id=str(restaurant.id),
        slug=restaurant.slug,
        total_views=total_views,
        views_today=views_today,
        views_last_7_days=views_last_7,
        views_last_30_days=views_last_30,
        daily_breakdown=daily_breakdown,
        hourly_breakdown=hourly_breakdown,
        device_breakdown=device_breakdown,
        browser_breakdown=browser_breakdown,
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        filtered_views=filtered_views,
    )


# ------------------------------------------------------------------ #
# ADMIN – get stats for the current user's restaurant
# ------------------------------------------------------------------ #
@router.get("/stats", response_model=MenuViewStats)
def get_menu_view_stats(
    start_date: Optional[date_type] = Query(None, description="Inicio del rango (YYYY-MM-DD)"),
    end_date: Optional[date_type] = Query(None, description="Fin del rango (YYYY-MM-DD)"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated view statistics for the admin's restaurant.

    **RF24** – pass ``start_date`` and ``end_date`` query-params to filter
    the daily breakdown and get ``filtered_views`` for the custom range.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date debe ser anterior o igual a end_date")

    return _build_stats(db, restaurant, start_date, end_date)


@router.get("/stats/{restaurant_id}", response_model=MenuViewStats)
def get_menu_view_stats_by_id(
    restaurant_id: UUID,
    start_date: Optional[date_type] = Query(None, description="Inicio del rango (YYYY-MM-DD)"),
    end_date: Optional[date_type] = Query(None, description="Fin del rango (YYYY-MM-DD)"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated view statistics for a specific restaurant (admin only).

    **RF24** – supports ``start_date`` / ``end_date`` query-params.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if restaurant.admin_id != user["id"] and user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date debe ser anterior o igual a end_date")

    return _build_stats(db, restaurant, start_date, end_date)


# ------------------------------------------------------------------ #
# CU-08 – CSV export
# ------------------------------------------------------------------ #
@router.get("/export")
def export_csv(
    start_date: Optional[date_type] = Query(None),
    end_date: Optional[date_type] = Query(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a CSV with one row per view event for the admin's restaurant."""

    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    q = db.query(MenuView).filter(MenuView.restaurant_id == restaurant.id)

    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="start_date debe ser anterior o igual a end_date")
        range_start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        range_end = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        q = q.filter(MenuView.viewed_at >= range_start, MenuView.viewed_at <= range_end)

    rows = q.order_by(MenuView.viewed_at.desc()).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "slug", "source", "user_agent", "dispositivo", "navegador", "referrer", "viewed_at"])

    for r in rows:
        writer.writerow([
            str(r.id),
            r.slug,
            r.source,
            r.user_agent or "",
            _classify_device(r.user_agent),
            _classify_browser(r.user_agent),
            r.referrer or "",
            r.viewed_at.isoformat() if r.viewed_at else "",
        ])

    buf.seek(0)
    filename = f"analytics_{restaurant.slug}"
    if start_date and end_date:
        filename += f"_{start_date}_{end_date}"
    filename += ".csv"

    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )