"""Tests for the analytics endpoints (RF22)."""

from __future__ import annotations

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
