from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import categories as categories_repo
from app.repositories import restaurants as restaurants_repo


class MenuServiceError(Exception):
    pass


class RestaurantNotFound(MenuServiceError):
    pass


@dataclass(frozen=True)
class PublicMenu:
    restaurant_slug: str
    categories_count: int


def get_public_menu_summary(db: Session, *, restaurant_slug: str) -> PublicMenu:
    restaurant = restaurants_repo.get_by_slug(db, restaurant_slug)
    if restaurant is None:
        raise RestaurantNotFound("Restaurant not found")

    categories = categories_repo.list_by_restaurant_id(db, restaurant.id)
    return PublicMenu(restaurant_slug=restaurant.slug, categories_count=len(categories))
