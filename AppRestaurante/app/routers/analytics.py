"""Frontend router for the analytics dashboard (RF22 / RF24 / CU-08)."""

import logging

import requests as http_requests
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from app.core.config import settings
from app.services.analytics_service import get_analytics_stats
from app.ui.templates import templates

router = APIRouter(prefix="/analytics", tags=["analytics"])

BACKEND_EXPORT_URL = f"{settings.BACKEND_URL}analytics/export"


@router.get("/export")
def export_csv(
    request: Request,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    """CU-08 – Proxy the CSV download from the backend API."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=303)

    params: dict[str, str] = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    try:
        resp = http_requests.get(
            BACKEND_EXPORT_URL,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=30,
        )
        if resp.status_code != 200:
            return RedirectResponse(url="/analytics", status_code=303)

        cd = resp.headers.get("content-disposition", 'attachment; filename="analytics.csv"')
        return StreamingResponse(
            iter([resp.content]),
            media_type="text/csv",
            headers={"Content-Disposition": cd},
        )
    except Exception as exc:
        logging.warning("CSV export proxy failed: %s", exc)
        return RedirectResponse(url="/analytics", status_code=303)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def analytics_dashboard(
    request: Request,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    """Render the analytics page for the restaurant admin.

    RF24 – accepts ``start_date`` / ``end_date`` query-params so the admin
    can filter the chart and table to a custom date range.
    """
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=303)

    stats = get_analytics_stats(token, start_date=start_date, end_date=end_date)

    return templates.TemplateResponse(
        "analytics/dashboard.html",
        {
            "request": request,
            "stats": stats,
            "start_date": start_date or "",
            "end_date": end_date or "",
        },
    )
