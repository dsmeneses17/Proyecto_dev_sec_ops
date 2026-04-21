import requests

from app.core.config import settings
from app.services.backend_auth import build_backend_headers


def _post_backend(url: str, payload: dict, timeout: int = 15):
    try:
        return requests.post(
            url,
            json=payload,
            headers=build_backend_headers(content_type_json=True),
            timeout=timeout,
        )
    except TypeError:
        # Backward-compatible with tests that monkeypatch requests.post without kwargs.
        try:
            return requests.post(url, json=payload, timeout=timeout)
        except TypeError:
            return requests.post(url, json=payload)


def autenticar_usuario(usuario: str, password: str):
    # Login al backend
    login_resp = _post_backend(
        f"{settings.BACKEND_URL}auth/login",
        {"usuario": usuario, "password": password},
        timeout=15,
    )

    if login_resp.status_code != 200:
        return {"error": "Credenciales inválidas"}

    # Usar SOLO la respuesta del backend
    login_data = login_resp.json()

    token = login_data["access_token"].strip()  # ← solo limpiar espacios
    rol = login_data["rol"]
    user_id = login_data["user_id"]
    restaurant_id = login_data.get("restaurant_id")
    restaurant_slug = login_data.get("restaurant_slug")

    return {
        "token": token,
        "rol": rol,
        "user_id": user_id,
        "restaurant_id": restaurant_id,
        "restaurant_slug": restaurant_slug
    }


def register_owner_with_restaurant(data: dict):
    """Register a new restaurant owner (admin) and their restaurant."""

    try:
        resp = _post_backend(f"{settings.BACKEND_URL}auth/register-owner", data, timeout=15)

        if resp.status_code != 200:
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = resp.text
            return {"error": detail or "No se pudo completar el registro"}

        return resp.json()
    except Exception:
        return {"error": "No se pudo conectar al servidor"}


def register_client(
    *,
    nombre_completo: str,
    usuario: str,
    email: str,
    password: str,
):
    """Register a new client user (no restaurant)."""

    try:
        resp = _post_backend(
            f"{settings.BACKEND_URL}auth/register",
            {
                "nombre_completo": nombre_completo,
                "usuario": usuario,
                "email": email,
                "password": password,
                "rol": "cliente",
            },
            timeout=15,
        )

        if resp.status_code == 422:
            # Pydantic validation errors
            detail = None
            try:
                body = resp.json()
                errors = body.get("detail", [])
                if isinstance(errors, list) and errors:
                    msgs = [e.get("msg", "") for e in errors]
                    detail = "; ".join(msgs)
                elif isinstance(errors, str):
                    detail = errors
            except Exception:
                detail = resp.text
            return {"error": detail or "Datos inválidos"}

        if resp.status_code != 200:
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = resp.text
            return {"error": detail or "No se pudo completar el registro"}

        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "No se pudo conectar al servidor"}
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}
