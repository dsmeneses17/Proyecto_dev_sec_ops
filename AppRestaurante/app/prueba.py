import requests

from app.models.restaurant_model import RestaurantCreate

# URL del backend
BACKEND_URL = "http://backend:5000/api/v1/admin/restaurants"

def enviar_restaurante(data: RestaurantCreate, token: str):
    """
    Envía los datos del restaurante al backend usando el token de autenticación.
    """
    # Quitar espacios extra por si acaso
    token = token.strip()

    headers = {
        "Authorization": f"Bearer {token}",  # Muy importante usar 'Bearer '
        "Content-Type": "application/json"
    }

    payload = data.model_dump()  # o data.dict() según tu versión de Pydantic

    print("Token final enviado:", token)
    print("Headers enviados:", headers)
    print("Payload enviado:", payload)

    try:
        response = requests.post(BACKEND_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("Error HTTP:", e, response.text)
        return {"error": True, "detalle": response.text}
    except Exception as e:
        print("Error inesperado :", e)
        return {"error": True, "detalle": str(e)}


if __name__ == "__main__":
    # Ejemplo de uso
    restaurante = RestaurantCreate(nombre="Mi Restaurante", direccion="Calle Falsa 123", slug="fdffd")
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Token que recibiste del login

    resultado = enviar_restaurante(restaurante, token)
    print("Resultado:", resultado)
