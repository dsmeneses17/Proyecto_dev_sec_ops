from fastapi import APIRouter, Request, HTTPException,   Form
import requests
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from app.utils.templates import get_template_context
from app.services.restaurant_service import enviar_a_backend_externo
from app.core.config import settings
from app.models.restaurant_model import RestaurantCreate, RestaurantOut   # <-- corregido
import logging
from app.core.config import settings
import json

router = APIRouter()

def get_headers(token: str):
    """Genera headers con Authorization Bearer"""
    # Limpiamos cualquier comilla accidental
    token = token.strip().strip("'").strip('"')
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token.strip()}"
    }


@router.get("/")
def mostrar_dashboard_restaurante(request: Request):
    # 🔹 Obtener token y rol de cookies
    #breakpoint()
    token = request.cookies.get("access_token")
    rol = request.cookies.get("rol")
    restaurant_id = request.cookies.get("restaurant_id")
    if not token or rol != "admin":
        # No autorizado → login
        return RedirectResponse(url="/", status_code=303)

    # 🔹 Llamar a la API para obtener los datos del restaurante del admin
    try:
        resp = requests.get(
            f"{settings.BACKEND_URL}admin/restaurants/restaurant/{restaurant_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
    except requests.exceptions.RequestException as e:
        # Error en la llamada a la API
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { "error": f"No se pudo conectar a la API: {e}",
             **get_template_context(request)}
        )

    if resp.status_code == 404:
        # No hay restaurante registrado → mostrar formulario para crear
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { **get_template_context(request)}
        )

    if resp.status_code != 200:
        # Otro error
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { "error": f"Error {resp.status_code} al obtener datos", **get_template_context(request)}
        )

    # 🔹 API respondió correctamente
    data = resp.json()
    # Si la API devuelve una lista, tomar el primer elemento
    restaurant_data = data[0] if isinstance(data, list) and len(data) > 0 else data

    return templates.TemplateResponse(
        "restaurants/restaurant.html",
        { "restaurant": restaurant_data, **get_template_context(request)}  # 👈 nombre correcto
    )

@router.get("/restaurant_form", response_class=HTMLResponse)
def restaurant_form(request: Request):
    token = request.cookies.get("access_token")
    restaurant_id = request.cookies.get("restaurant_id")
    if not token or not restaurant_id:
        return RedirectResponse(url="/", status_code=303)

    # Llamar a la API
    try:
        resp = requests.get(
            f"{settings.BACKEND_URL}admin/restaurants/restaurant/{restaurant_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
       
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { "error": f"No se pudo conectar a la API: {e}",
             **get_template_context(request)}
        )

    if resp.status_code != 200:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { "error": f"Error {resp.status_code} al obtener datos",
             **get_template_context(request)}
        )

    restaurant_data = resp.json()
    print(restaurant_data)
    return templates.TemplateResponse(
        "restaurants/restaurant_form.html",
        { "restaurant": restaurant_data,
         **get_template_context(request)}
    )

@router.post("/restaurant", response_model=RestaurantOut)
def create_restaurant(
    request: Request,
    nombre: str = Form(...),
    slug: str = Form(...),
    logo: str = Form(...),
    descripcion: str = Form(None),
    telefono: str = Form(None),
    direccion: str = Form(None),
    horarios: str = Form("{}")
):
    token = request.cookies.get("access_token")
    restaurant_id = request.cookies.get("restaurant_id")
    if not token:
        raise HTTPException(status_code=200, detail="Token requerido")

    # convertir horarios si es JSON válido
    try:
        horarios_dict = json.loads(horarios)
    except Exception:
        horarios_dict = {}



    # 🔥 NORMALIZAR AQUÍ
    if restaurant_id in ["None", "", None]:
        restaurant_id = None


    restaurant = RestaurantCreate(
        id=restaurant_id,
        nombre=nombre,
        slug=slug,
        logo=logo,
        descripcion=descripcion,
        telefono=telefono,
        direccion=direccion,
        horarios=horarios_dict
    )


    resultado = enviar_a_backend_externo(restaurant, token)
    if "error" in resultado:
        raise HTTPException(status_code=200, detail=resultado)

    return resultado  # 👉 devuelve JSON con el restaurante creado



@router.post("/send") 
def send_data(data: dict): 
    return enviar_a_backend_externo(data)
