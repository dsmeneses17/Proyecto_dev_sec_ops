"""Frontend router for the analytics dashboard (RF22)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.ui.templates import templates
from app.services.analytics_service import get_analytics_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def analytics_dashboard(request: Request):
    """Render the analytics page for the restaurant admin."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/", status_code=303)

    stats = get_analytics_stats(token)

    return templates.TemplateResponse(
        "analytics/dashboard.html",
        {
            "request": request,
            "stats": stats,
        },
    )
