import logging

import requests

from app.core.config import settings
from app.services.backend_auth import build_backend_headers

# URL del backend
BACKEND_URL = f"{settings.BACKEND_URL}admin/categories/"


def get_headers(token: str):
    """Genera headers con Authorization Bearer + IAM interno."""
    return build_backend_headers(user_token=token, content_type_json=True)


def list_categorias(token: str):
    """Lista categorías usando token enviado al backend"""
    try:
        response = requests.get(
            f"{settings.BACKEND_URL}admin/categories/",  # slash final obligatorio
            headers=get_headers(token),
            timeout=10,
        )

        print("TOKEN ENVIADO AL BACKEND listar:", token)
        print("STATUS:", response.status_code)
        print("TEXT:", response.text[:200])

        if response.status_code != 200:
            return {
                "error": True,
                "detalle": response.json()
                if "application/json" in response.headers.get("content-type", "")
                else response.text,
                "status_code": response.status_code,
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error("Error al conectar con el backend: %s", str(e))
        return {"error": True, "detalle": str(e), "status_code": None}


def get_categoria(token: str, categoria_id: str):
    """Obtiene una categoría por ID desde el backend"""
    url = f"{settings.BACKEND_URL}admin/categories/{categoria_id}"
    try:
        response = requests.get(url, headers=get_headers(token), timeout=10)

        print("URL:", url)
        print("STATUS:", response.status_code)
        print("TEXT:", response.text[:200])

        if response.status_code != 200:
            return {
                "error": True,
                "detalle": response.json()
                if "application/json" in response.headers.get("content-type", "")
                else response.text,
                "status_code": response.status_code,
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error("Error al conectar con el backend: %s", str(e))
        return {"error": True, "detalle": str(e), "status_code": None}


def create_categoria(token: str, data):
    """Crea una categoría en el backend"""
    payload = data if isinstance(data, dict) else data.model_dump(exclude_none=True)
    try:
        response = requests.post(BACKEND_URL, json=payload, headers=get_headers(token), timeout=10)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        detalle = e.response.text
        if status == 401:
            detalle = "Unauthorized: Token inválido o expirado"
        return {"error": True, "detalle": detalle, "status_code": status}


def update_categoria(token: str, categoria_id: str, payload: dict):
    url = f"{BACKEND_URL}{categoria_id}"  # Importante slash
    try:
        response = requests.put(url, json=payload, headers=get_headers(token), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error("Error HTTP %s: %s", e.response.status_code, e.response.text)
        return {"error": True, "detalle": e.response.text, "status_code": e.response.status_code}


def delete_categoria(token: str, categoria_id: str):
    url = f"{BACKEND_URL}{categoria_id}"  # Importante el slash
    try:
        response = requests.delete(url, headers=get_headers(token), timeout=10)
        response.raise_for_status()
        return {"deleted": True}
    except requests.exceptions.HTTPError as e:
        logging.error("Error HTTP %s: %s", e.response.status_code, e.response.text)
        return {"error": True, "detalle": e.response.text, "status_code": e.response.status_code}


def reorder_categorias(token: str, payload: dict):
    url = f"{BACKEND_URL}reorder"  # Importante el slash
    try:
        response = requests.patch(url, json=payload, headers=get_headers(token), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error("Error HTTP %s: %s", e.response.status_code, e.response.text)
        return {"error": True, "detalle": e.response.text, "status_code": e.response.status_code}
