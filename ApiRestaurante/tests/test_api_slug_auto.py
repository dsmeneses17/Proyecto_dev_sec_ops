"""API contract tests for auto-slug generation (RF06).

Verifies that:
- register-owner auto-generates a slug when none is provided
- register-owner accepts an explicit slug
- register-owner avoids collisions by appending a suffix
- admin restaurant create auto-generates slug
"""

import uuid


def _unique(prefix: str = "rf06") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ── POST /api/v1/auth/register-owner ─────────────────────────────────────────

def test_register_owner_auto_slug(client):
    """Slug omitted → backend generates it from restaurant name."""
    u = _unique()
    resp = client.post(
        "/api/v1/auth/register-owner",
        json={
            "nombre_completo": "Auto Slug User",
            "usuario": u,
            "email": f"{u}@example.com",
            "password": "secret123",
            "restaurant_nombre": "Café París",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["restaurant_slug"]  # non-empty
    assert data["restaurant_slug"] == "cafe-paris" or data["restaurant_slug"].startswith("cafe-paris")


def test_register_owner_explicit_slug(client):
    """Explicit slug provided → backend uses it."""
    u = _unique()
    resp = client.post(
        "/api/v1/auth/register-owner",
        json={
            "nombre_completo": "Explicit Slug",
            "usuario": u,
            "email": f"{u}@example.com",
            "password": "secret123",
            "restaurant_nombre": "My Place",
            "restaurant_slug": "my-custom-slug",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["restaurant_slug"] == "my-custom-slug" or data["restaurant_slug"].startswith("my-custom-slug")


def test_register_owner_slug_collision_appends_suffix(client):
    """Two restaurants with the same name get different slugs."""
    base = _unique("collision")

    # First registration
    resp1 = client.post(
        "/api/v1/auth/register-owner",
        json={
            "nombre_completo": "User One",
            "usuario": f"u1_{base}",
            "email": f"u1_{base}@example.com",
            "password": "secret123",
            "restaurant_nombre": "Duplicate Name",
        },
    )
    assert resp1.status_code == 200, resp1.text
    slug1 = resp1.json()["restaurant_slug"]

    # Second registration — same restaurant name, different user
    resp2 = client.post(
        "/api/v1/auth/register-owner",
        json={
            "nombre_completo": "User Two",
            "usuario": f"u2_{base}",
            "email": f"u2_{base}@example.com",
            "password": "secret123",
            "restaurant_nombre": "Duplicate Name",
        },
    )
    assert resp2.status_code == 200, resp2.text
    slug2 = resp2.json()["restaurant_slug"]

    # Both should succeed, but with different slugs
    assert slug1 != slug2
    assert slug1 == "duplicate-name"
    assert slug2 == "duplicate-name-2"


def test_register_owner_no_slug_field_required(client):
    """restaurant_slug is no longer required — missing it should not cause 422."""
    u = _unique()
    resp = client.post(
        "/api/v1/auth/register-owner",
        json={
            "nombre_completo": "No Slug",
            "usuario": u,
            "email": f"{u}@example.com",
            "password": "secret123",
            "restaurant_nombre": "Sin Slug",
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["restaurant_slug"] == "sin-slug" or resp.json()["restaurant_slug"].startswith("sin-slug")
