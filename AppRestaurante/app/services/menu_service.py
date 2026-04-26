import requests

from app.core.config import settings
from app.models.menu import PublicMenuResponse
from app.services.backend_auth import build_backend_headers
from app.services.storage import build_display_url

# settings.BACKEND_URL already includes the trailing `/api/v1/`
API_BASE = f"{settings.BACKEND_URL}public/menu"


def _sign_menu_images(data: dict) -> dict:
    if not isinstance(data, dict):
        return data

    restaurant = data.get("restaurant")
    if isinstance(restaurant, dict) and restaurant.get("logo_url"):
        restaurant["logo_url"] = build_display_url(restaurant["logo_url"])

    categories = data.get("categorias", [])
    if isinstance(categories, list):
        for category in categories:
            if not isinstance(category, dict):
                continue
            dishes = category.get("platos", [])
            if not isinstance(dishes, list):
                continue
            for dish in dishes:
                if isinstance(dish, dict) and dish.get("imagen_url"):
                    dish["imagen_url"] = build_display_url(dish["imagen_url"])

    return data


def get_public_menu(slug: str) -> PublicMenuResponse | None:
    try:
        response = requests.get(f"{API_BASE}/{slug}", headers=build_backend_headers(), timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        data = _sign_menu_images(data)
        return PublicMenuResponse(**data)

    except Exception as e:
        print("Error consumiendo API:", e)
        return None


def list_public_restaurants() -> list[dict]:
    """Fetch restaurant slugs/names for the public menu selector.

    Returns a list like: [{"slug": "...", "nombre": "...", ...}, ...]
    """

    try:
        response = requests.get(f"{API_BASE}/restaurants", timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []
