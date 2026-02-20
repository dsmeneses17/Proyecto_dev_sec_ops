import requests
from app.core.config import settings
from app.core.security import decode_token

def autenticar_usuario(usuario: str, password: str):
    # 1️⃣ Login al backend
    login_resp = requests.post(
        f"{settings.BACKEND_URL}auth/login",
        json={"usuario": usuario, "password": password}
    )

    if login_resp.status_code != 200:
        return {"error": "❌ Credenciales inválidas"}

    # 2️⃣ Usar SOLO la respuesta del backend
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
