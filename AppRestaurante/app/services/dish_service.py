# app/services/dish_service.py
import requests
import logging
from app.core.config import settings

# URL del backend de platos
BACKEND_URL = f"{settings.BACKEND_URL}admin/dishes/"


def get_headers(token: str):
    """Genera headers con Authorization Bearer"""
    token = token.strip().strip("'").strip('"')
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

def list_dishes(token: str, categoria_id: str = None):
    """
    Lista platos agrupados por categoría.
    Si categoria_id se pasa, se filtra solo esa categoría.
    """
    try:
        url = BACKEND_URL + "by_category"
        if categoria_id:
            url += f"?categoria_id={categoria_id}"

        response = requests.get(url, headers=get_headers(token), timeout=10)
        if response.status_code != 200:
            return {
                "error": True,
                "detalle": response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
                "status_code": response.status_code
            }
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("❌ Error al conectar con backend: %s", e)
        return {"error": True, "detalle": str(e), "status_code": None}


def get_dish(token: str, dish_id: str):
    """Obtiene un plato por ID"""
    try:
        response = requests.get(f"{BACKEND_URL}{dish_id}", headers=get_headers(token), timeout=10)
        if response.status_code != 200:
            return {"error": True, "detalle": response.text, "status_code": response.status_code}
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("❌ Error al conectar con backend: %s", e)
        return {"error": True, "detalle": str(e), "status_code": None}


def create_dish(token: str, payload: dict):
    response = requests.post(
        BACKEND_URL, 
        json=payload,
        headers=get_headers(token),
        timeout=10
    )
    if response.status_code not in [200, 201]:
        return {"error": True, "detalle": response.text, "status_code": response.status_code}
    return response.json()


def update_dish(token: str, dish_id: str, payload: dict):
    response = requests.put(
        f"{BACKEND_URL}{dish_id}",
        json=payload,
        headers=get_headers(token),
        timeout=10
    )
    if response.status_code != 200:
        return {"error": True, "detalle": response.text, "status_code": response.status_code}
    return response.json()


def delete_dish(token: str, dish_id: str):
    """Soft delete de un plato"""
    try:
        response = requests.delete(f"{BACKEND_URL}{dish_id}", headers=get_headers(token), timeout=10)
        if response.status_code not in [200, 204]:
            return {"error": True, "detalle": response.text, "status_code": response.status_code}
        return {"deleted": True}
    except requests.exceptions.RequestException as e:
        logging.error("❌ Error al conectar con backend: %s", e)
        return {"error": True, "detalle": str(e), "status_code": None}


def toggle_availability(token: str, dish_id: str):
    """Cambia disponibilidad de un plato"""
    try:
        response = requests.patch(f"{BACKEND_URL}{dish_id}/toggle_availability", headers=get_headers(token), timeout=10)
        if response.status_code != 200:
            return {"error": True, "detalle": response.text, "status_code": response.status_code}
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("❌ Error al conectar con backend: %s", e)
        return {"error": True, "detalle": str(e), "status_code": None}
