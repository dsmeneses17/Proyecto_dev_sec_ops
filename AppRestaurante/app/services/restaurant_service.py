import json
import logging

import requests

from app.core.config import settings
from app.models.restaurant_model import RestaurantCreate


BACKEND_URL = f"{settings.BACKEND_URL}admin/restaurants/restaurant"


def _build_headers(token: str | None) -> dict:
    safe_token = (token or "").strip()
    return {
        "Authorization": f"Bearer {safe_token}",
        "Content-Type": "application/json",
    }


def _normalize_payload(data: RestaurantCreate | dict) -> dict:
    if isinstance(data, RestaurantCreate):
        payload = data.model_dump(mode="json", exclude_none=True)
    elif isinstance(data, dict):
        payload = dict(data)
    else:
        raise ValueError("Formato de restaurante inválido")

    if payload.get("id") in ["None", "", None]:
        payload.pop("id", None)

    if "horarios" in payload:
        try:
            if isinstance(payload["horarios"], str):
                payload["horarios"] = json.loads(payload["horarios"])
        except Exception:
            payload["horarios"] = {}

    return payload


def get_restaurant_by_id(token: str, restaurant_id: str):
    try:
        response = requests.get(
            f"{BACKEND_URL}/{restaurant_id}",
            headers=_build_headers(token),
            timeout=10,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Error consultando restaurante: %s", e)
        return {"error": True, "detalle": "No se pudo consultar el restaurante"}


def create_or_update_restaurant(data: RestaurantCreate | dict, token: str | None = None):
    if token:
        token = token.strip()
        if not token.startswith("ey"):
            logging.warning("⚠️ Token parece inválido: %s", token)
            return {"error": True, "detalle": "Token inválido"}
        token = "".join(token.split())

    payload = _normalize_payload(data)

    try:
        response = requests.post(
            BACKEND_URL,
            json=payload,
            headers=_build_headers(token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError as e:
        logging.error("Error de conexión con el backend: %s", e)
        return {"error": True, "detalle": "No se pudo conectar al backend"}

    except requests.exceptions.HTTPError as e:
        logging.error(
            "Error HTTP: %s - %s",
            e,
            response.text if "response" in locals() else "",
        )
        return {
            "error": True,
            "detalle": str(e),
            "backend": response.text if "response" in locals() else "",
        }

    except Exception as e:
        logging.error("Error inesperado: %s", e)
        return {"error": True, "detalle": str(e)}


def delete_restaurant(token: str, restaurant_id: str):
    try:
        response = requests.delete(
            f"{BACKEND_URL}/{restaurant_id}",
            headers=_build_headers(token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json() if response.content else {"message": "Restaurante eliminado"}
    except requests.exceptions.HTTPError as e:
        logging.error(
            "Error HTTP al eliminar restaurante: %s - %s",
            e,
            response.text if "response" in locals() else "",
        )
        return {
            "error": True,
            "detalle": str(e),
            "backend": response.text if "response" in locals() else "",
        }
    except requests.exceptions.RequestException as e:
        logging.error("Error eliminando restaurante: %s", e)
        return {"error": True, "detalle": "No se pudo eliminar el restaurante"}



def enviar_a_backend_externo(data: RestaurantCreate, token: str = None):
    return create_or_update_restaurant(data, token)


def update_restaurant_colors(token: str, restaurant_id: str, qr_color_fg: str, qr_color_bg: str):
    """
    Update QR colors for a restaurant
    """
    try:
        payload = {
            "qr_color_fg": qr_color_fg,
            "qr_color_bg": qr_color_bg,
        }
        
        response = requests.patch(
            f"{BACKEND_URL}/{restaurant_id}",
            headers=_build_headers(token),
            json=payload,
            timeout=10,
        )

        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {
                "error": True,
                "detalle": response.json().get("detail", "Error al actualizar colores"),
            }
    except requests.exceptions.Timeout:
        logging.error("Timeout al actualizar colores del restaurante")
        return {"error": True, "detalle": "Timeout en la solicitud"}
    except requests.exceptions.RequestException as e:
        logging.error("Error actualizando colores del restaurante: %s", e)
        return {"error": True, "detalle": "No se pudieron actualizar los colores"}