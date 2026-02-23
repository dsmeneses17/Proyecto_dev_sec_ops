import requests
from app.models.menu import PublicMenuResponse
from app.core.config import settings

# settings.BACKEND_URL already includes the trailing `/api/v1/`
API_BASE = f"{settings.BACKEND_URL}public/menu"


def get_public_menu(slug: str) -> PublicMenuResponse | None:
    try:
        response = requests.get(f"{API_BASE}/{slug}")

        if response.status_code != 200:
            return None

        data = response.json()
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
