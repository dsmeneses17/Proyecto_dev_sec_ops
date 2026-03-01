"""Tests for the analytics endpoints (RF22 / RF24 / CU-08)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


# ------------------------------------------------------------------ public
def test_record_view_returns_201(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="p", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    r = client.post(
        "/api/v1/analytics/views",
        json={"slug": "test-resto", "source": "menu"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["slug"] == "test-resto"
    assert body["source"] == "menu"
    assert "id" in body
    assert "viewed_at" in body


def test_record_view_unknown_slug_is_404(client):
    r = client.post(
        "/api/v1/analytics/views",
        json={"slug": "no-existe", "source": "menu"},
    )
    assert r.status_code == 404


def test_record_view_invalid_source_is_422(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="p", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    r = client.post(
        "/api/v1/analytics/views",
        json={"slug": "test-resto", "source": "invalid_source"},
    )
    assert r.status_code == 422


def test_record_multiple_views(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="p", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    for source in ("menu", "qr", "direct"):
        r = client.post(
            "/api/v1/analytics/views",
            json={"slug": "test-resto", "source": source},
        )
        assert r.status_code == 201


# ------------------------------------------------------------------ admin stats
def _login(client, usuario: str, password: str) -> str:
    r = client.post(
        "/api/v1/auth/login",
        json={"usuario": usuario, "password": password},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_stats_requires_auth(client):
    r = client.get("/api/v1/analytics/stats")
    assert r.status_code in (401, 403)


def test_stats_returns_zeroes_with_no_views(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")
    token = _login(client, "admin", "adminpass")

    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_views"] == 0
    assert body["views_today"] == 0
    assert body["views_last_7_days"] == 0
    assert body["views_last_30_days"] == 0
    assert body["slug"] == "test-resto"


def test_stats_counts_recorded_views(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    # Record 3 views
    for _ in range(3):
        client.post(
            "/api/v1/analytics/views",
            json={"slug": "test-resto", "source": "menu"},
        )

    token = _login(client, "admin", "adminpass")
    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_views"] == 3
    assert body["views_today"] == 3
    assert body["views_last_7_days"] == 3
    assert body["views_last_30_days"] == 3
    assert isinstance(body["daily_breakdown"], list)
    assert len(body["daily_breakdown"]) >= 1


def test_stats_by_id_requires_ownership(client, make_user, make_restaurant):
    admin1 = make_user(usuario="admin1", password="adminpass", rol="admin")
    other = make_user(usuario="other", password="otherpass", rol="cliente", email="o@test.com")
    rest = make_restaurant(admin_id=admin1.id, slug="test-resto", nombre="Test Resto")

    token_other = _login(client, "other", "otherpass")
    r = client.get(
        f"/api/v1/analytics/stats/{rest.id}",
        headers={"Authorization": f"Bearer {token_other}"},
    )
    assert r.status_code == 403


# ------------------------------------------------------------------ RF24: date-range filtering
def test_stats_with_date_range_filters_breakdown(client, make_user, make_restaurant, db_session):
    """When start_date/end_date are provided, daily_breakdown and
    filtered_views are scoped to that range while KPI cards stay global."""
    from app.models.menu_view import MenuView

    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    rest = make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    now = datetime.now(timezone.utc)

    # Insert views at different dates: 2 old (15 days ago) + 3 recent (today)
    for i in range(2):
        db_session.add(MenuView(
            restaurant_id=rest.id,
            slug="test-resto",
            source="menu",
            viewed_at=now - timedelta(days=15, hours=i),
        ))
    for i in range(3):
        db_session.add(MenuView(
            restaurant_id=rest.id,
            slug="test-resto",
            source="qr",
            viewed_at=now - timedelta(hours=i),
        ))
    db_session.commit()

    token = _login(client, "admin", "adminpass")

    # Filter to only today
    today_str = now.strftime("%Y-%m-%d")
    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": today_str, "end_date": today_str},
    )
    assert r.status_code == 200
    body = r.json()

    # KPI cards are still global
    assert body["total_views"] == 5
    # filtered_views should only count today's 3
    assert body["filtered_views"] == 3
    assert body["start_date"] == today_str
    assert body["end_date"] == today_str
    # daily_breakdown should only have 1 entry (today)
    assert len(body["daily_breakdown"]) == 1
    assert body["daily_breakdown"][0]["views"] == 3


def test_stats_date_range_returns_empty_for_no_data(client, make_user, make_restaurant):
    """A range with no views returns an empty breakdown and filtered_views=0."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    token = _login(client, "admin", "adminpass")

    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": "2020-01-01", "end_date": "2020-01-31"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["filtered_views"] == 0
    assert body["daily_breakdown"] == []
    assert body["start_date"] == "2020-01-01"
    assert body["end_date"] == "2020-01-31"


def test_stats_invalid_date_range_returns_400(client, make_user, make_restaurant):
    """start_date > end_date should return 400."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    token = _login(client, "admin", "adminpass")

    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": "2026-03-10", "end_date": "2026-03-01"},
    )
    assert r.status_code == 400


def test_stats_no_date_range_returns_no_filtered_fields(client, make_user, make_restaurant):
    """Without date params, filtered_views / start_date / end_date are null."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    token = _login(client, "admin", "adminpass")

    r = client.get(
        "/api/v1/analytics/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["filtered_views"] is None
    assert body["start_date"] is None
    assert body["end_date"] is None


def test_stats_by_id_with_date_range(client, make_user, make_restaurant, db_session):
    """The /stats/{restaurant_id} endpoint also supports date-range filtering."""
    from app.models.menu_view import MenuView

    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    rest = make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    now = datetime.now(timezone.utc)
    for i in range(4):
        db_session.add(MenuView(
            restaurant_id=rest.id,
            slug="test-resto",
            source="direct",
            viewed_at=now - timedelta(days=i),
        ))
    db_session.commit()

    token = _login(client, "admin", "adminpass")

    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    r = client.get(
        f"/api/v1/analytics/stats/{rest.id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": yesterday_str, "end_date": today_str},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["filtered_views"] == 2
    assert body["total_views"] == 4


# ------------------------------------------------------------------ CU-08: ip_hash, referrer, hourly, device, csv

def test_record_view_hashes_ip(client, make_user, make_restaurant):
    """The ip_hash field should be a SHA-256 hex digest, not the raw IP."""
    admin = make_user(usuario="admin", password="p", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    r = client.post(
        "/api/v1/analytics/views",
        json={"slug": "test-resto", "source": "menu"},
    )
    assert r.status_code == 201
    body = r.json()
    # ip_hash should be 64 hex chars (SHA-256) or None – never a raw IP
    if body["ip_hash"]:
        assert len(body["ip_hash"]) == 64
        assert all(c in "0123456789abcdef" for c in body["ip_hash"])


def test_stats_include_hourly_breakdown(client, make_user, make_restaurant):
    """Stats response must include hourly_breakdown with 24 entries."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    # Record a view so there's data
    client.post("/api/v1/analytics/views", json={"slug": "test-resto", "source": "menu"})

    token = _login(client, "admin", "adminpass")
    r = client.get("/api/v1/analytics/stats", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()

    assert "hourly_breakdown" in body
    assert len(body["hourly_breakdown"]) == 24
    assert body["hourly_breakdown"][0]["hour"] == 0
    assert body["hourly_breakdown"][23]["hour"] == 23
    # At least one hour should have views > 0
    assert any(h["views"] > 0 for h in body["hourly_breakdown"])


def test_stats_include_device_and_browser_breakdown(client, make_user, make_restaurant):
    """Stats must include device_breakdown and browser_breakdown."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    client.post("/api/v1/analytics/views", json={"slug": "test-resto", "source": "menu"})

    token = _login(client, "admin", "adminpass")
    r = client.get("/api/v1/analytics/stats", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()

    assert "device_breakdown" in body
    assert "browser_breakdown" in body
    assert len(body["device_breakdown"]) >= 1
    assert len(body["browser_breakdown"]) >= 1
    # Each entry has name, count, percentage
    for d in body["device_breakdown"]:
        assert "name" in d and "count" in d and "percentage" in d


def test_csv_export_requires_auth(client):
    """CSV export without token should fail."""
    r = client.get("/api/v1/analytics/export")
    assert r.status_code in (401, 403)


def test_csv_export_returns_csv(client, make_user, make_restaurant):
    """CSV export returns a text/csv response with expected headers."""
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    # Record some views
    for src in ("menu", "qr", "direct"):
        client.post("/api/v1/analytics/views", json={"slug": "test-resto", "source": src})

    token = _login(client, "admin", "adminpass")
    r = client.get(
        "/api/v1/analytics/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "attachment" in r.headers.get("content-disposition", "")

    # Parse CSV content
    text = r.text
    lines = text.strip().split("\n")
    assert len(lines) == 4  # 1 header + 3 data rows
    header = lines[0]
    assert "slug" in header
    assert "dispositivo" in header
    assert "navegador" in header


def test_csv_export_with_date_filter(client, make_user, make_restaurant, db_session):
    """CSV export with date range only includes rows in that range."""
    from app.models.menu_view import MenuView

    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    rest = make_restaurant(admin_id=admin.id, slug="test-resto", nombre="Test Resto")

    now = datetime.now(timezone.utc)
    # 2 old + 1 today
    db_session.add(MenuView(restaurant_id=rest.id, slug="test-resto", source="menu",
                            viewed_at=now - timedelta(days=20)))
    db_session.add(MenuView(restaurant_id=rest.id, slug="test-resto", source="qr",
                            viewed_at=now - timedelta(days=20)))
    db_session.add(MenuView(restaurant_id=rest.id, slug="test-resto", source="direct",
                            viewed_at=now))
    db_session.commit()

    token = _login(client, "admin", "adminpass")

    today_str = now.strftime("%Y-%m-%d")
    r = client.get(
        "/api/v1/analytics/export",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": today_str, "end_date": today_str},
    )
    assert r.status_code == 200
    lines = r.text.strip().split("\n")
    assert len(lines) == 2  # 1 header + 1 data row
