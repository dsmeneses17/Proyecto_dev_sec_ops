"""Service for menu-view analytics (RF22).

The frontend fires a non-blocking POST to the backend every time a public
menu page is rendered so every visualisation is registered.
"""

import logging

import requests

from app.core.config import settings

ANALYTICS_URL = f"{settings.BACKEND_URL}analytics"


def record_menu_view(slug: str, source: str = "menu") -> None:
    """Fire-and-forget: tell the backend that a menu was viewed.

    Failures are silently logged – they must never break the public page.
    """
    try:
        requests.post(
            f"{ANALYTICS_URL}/views",
            json={"slug": slug, "source": source},
            timeout=3,
        )
    except Exception as exc:
        logging.warning("analytics record_menu_view failed: %s", exc)


def get_analytics_stats(token: str, start_date: str | None = None, end_date: str | None = None) -> dict | None:
    """Fetch aggregated stats for the admin's restaurant.

    RF24 – optionally pass ``start_date`` / ``end_date`` (YYYY-MM-DD) to
    filter the daily breakdown and get ``filtered_views``.
    """
    try:
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        resp = requests.get(
            f"{ANALYTICS_URL}/stats",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        logging.warning("analytics stats returned %s", resp.status_code)
        return None
    except Exception as exc:
        logging.warning("analytics get_stats failed: %s", exc)
        return None
