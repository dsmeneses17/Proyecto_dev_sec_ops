import requests
from app.models.restaurant_model import RestaurantCreate
import logging
import requests
import json
from pydantic import  HttpUrl
from app.core.config import settings

BACKEND_URL = f"{settings.BACKEND_URL}admin/restaurants/restaurant"


def enviar_a_backend_externo(data: RestaurantCreate, token: str = None):

    if token:
        token = token.strip()
        if not token.startswith("ey"):
            logging.warning("⚠️ Token parece inválido: %s", token)
            return {"error": True, "detalle": "Token inválido"}
        token = "".join(token.split())

    # 🔥 IMPORTANTE: usar mode="json"
    payload = data.model_dump(mode="json", exclude_none=True)

    # 🔥 Normalizar ID si vino como string "None"
    if payload.get("id") in ["None", "", None]:
        payload.pop("id", None)

    # 🔹 Asegurarse de que horarios sea un dict
    if "horarios" in payload:
        try:
            # si es string, parsear como JSON
            if isinstance(payload["horarios"], str):
                payload["horarios"] = json.loads(payload["horarios"])
        except Exception:
            # si falla, usar dict vacío
            payload["horarios"] = {}
            
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"token final enviado: {token}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(BACKEND_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError as e:
        logging.error("❌ Error de conexión con el backend: %s", e)
        return {"error": True, "detalle": "No se pudo conectar al backend"}

    except requests.exceptions.HTTPError as e:
        logging.error(
            "❌ Error HTTP: %s - %s",
            e,
            response.text if 'response' in locals() else ""
        )
        return {
            "error": True,
            "detalle": str(e),
            "backend": response.text if 'response' in locals() else ""
        }

    except Exception as e:
        logging.error("❌ Error inesperado: %s", e)
        return {"error": True, "detalle": str(e)}