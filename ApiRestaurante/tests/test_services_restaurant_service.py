from unittest.mock import Mock

import pytest

from app.services import restaurant_service


def test_create_restaurant_raises_when_slug_exists(monkeypatch):
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


def test_create_restaurant_returns_payload_when_slug_free(monkeypatch):
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
