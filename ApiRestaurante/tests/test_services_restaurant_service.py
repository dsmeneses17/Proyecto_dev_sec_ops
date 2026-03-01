from unittest.mock import Mock

import pytest

from app.services import restaurant_service

pytestmark = pytest.mark.no_db


def test_create_restaurant_raises_when_explicit_slug_exists(monkeypatch):
    db = Mock()
    monkeypatch.setattr(restaurant_service.restaurants_repo, "get_by_slug", lambda *_: object())

    with pytest.raises(restaurant_service.RestaurantSlugAlreadyExists):
        restaurant_service.create_restaurant(
            db,
            restaurant_service.CreateRestaurantInput(
                nombre="R",
                slug="same",
                admin_id=1,
            ),
        )


def test_create_restaurant_returns_payload_when_explicit_slug_free(monkeypatch):
    db = Mock()
    monkeypatch.setattr(restaurant_service.restaurants_repo, "get_by_slug", lambda *_: None)

    result = restaurant_service.create_restaurant(
        db,
        restaurant_service.CreateRestaurantInput(
            nombre="R",
            slug="free",
            admin_id=1,
            telefono="123",
        ),
    )
    assert result["slug"] == "free"
    assert result["admin_id"] == 1
    assert result["telefono"] == "123"


def test_create_restaurant_auto_generates_slug_from_nombre(monkeypatch):
    """When slug is not provided, it should be auto-generated from nombre."""
    db = Mock()
    # generate_unique_slug will query the DB — mock it at the module level
    monkeypatch.setattr(
        restaurant_service,
        "generate_unique_slug",
        lambda _db, nombre: "mi-restaurante",
    )

    result = restaurant_service.create_restaurant(
        db,
        restaurant_service.CreateRestaurantInput(
            nombre="Mi Restaurante",
            admin_id=1,
        ),
    )
    assert result["slug"] == "mi-restaurante"
    assert result["admin_id"] == 1
