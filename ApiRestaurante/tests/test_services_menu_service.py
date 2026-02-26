from unittest.mock import Mock

import pytest

from app.services import menu_service


def test_get_public_menu_summary_raises_if_restaurant_missing(monkeypatch):
    db = Mock()
    monkeypatch.setattr(menu_service.restaurants_repo, "get_by_slug", lambda *_: None)

    with pytest.raises(menu_service.RestaurantNotFound):
        menu_service.get_public_menu_summary(db, restaurant_slug="nope")


def test_get_public_menu_summary_counts_categories(monkeypatch):
    db = Mock()
    restaurant = Mock(id="rid", slug="slug")
    monkeypatch.setattr(menu_service.restaurants_repo, "get_by_slug", lambda *_: restaurant)
    monkeypatch.setattr(menu_service.categories_repo, "list_by_restaurant_id", lambda *_: [1, 2, 3])

    result = menu_service.get_public_menu_summary(db, restaurant_slug="slug")
    assert result.restaurant_slug == "slug"
    assert result.categories_count == 3
