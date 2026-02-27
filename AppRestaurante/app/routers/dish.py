# app/routers/dish.py
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from app.utils.templates import get_template_context
from typing import Optional
from types import SimpleNamespace
import jwt

from app.services.dish_service import (
    list_dishes,
    get_dish,
    create_dish,
    update_dish,
    delete_dish,
    toggle_availability
)
from app.services.storage import build_display_url

router = APIRouter(tags=["platos"])


def _sign_dish_images(categorias):
    if not isinstance(categorias, list):
        return categorias

    for categoria in categorias:
        platos = categoria.get("platos", []) if isinstance(categoria, dict) else []
        for plato in platos:
            if isinstance(plato, dict) and plato.get("imagen_url"):
                plato["imagen_url"] = build_display_url(plato["imagen_url"])
    return categorias


@router.get("", response_class=HTMLResponse)
def listar(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    resultado = list_dishes(token)

    if isinstance(resultado, dict) and "error" in resultado:
        categorias = []
        error = resultado.get("detalle", "Error al cargar platos")
    else:
        categorias = _sign_dish_images(resultado)
        error = None

    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "categorias": categorias,
            "plato": None,
            "error": error,
            "success": None,
            **get_template_context(request)
        }
    )


@router.get("/{dish_id}", response_class=HTMLResponse)
def editar_form(request: Request, dish_id: str):
    """
    Obtiene un plato por ID para edición
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    plato_obj = get_dish(token, dish_id)
    if "error" in plato_obj:
        raise HTTPException(status_code=400, detail=plato_obj["detalle"])

    if plato_obj.get("imagen_url"):
        plato_obj["imagen_url"] = build_display_url(plato_obj["imagen_url"])

    plato = SimpleNamespace(**plato_obj)
    categorias = _sign_dish_images(list_dishes(token))
    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "categorias": categorias,
            "plato": plato,
            "error": None,
            "success": None,
            **get_template_context(request)
        }
    )


@router.post("", response_class=HTMLResponse)
def crear(
    request: Request,
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: float = Form(...),
    precio_oferta: Optional[float] = Form(None),
    imagen_url: Optional[str] = Form(None),
    categoria_id: str = Form(...),
    disponible: Optional[bool] = Form(True),
    destacado: Optional[bool] = Form(False),
    etiquetas: Optional[str] = Form(None),
    posicion: Optional[int] = Form(None),
    plato_id: Optional[str] = Form(None)
):
    """
    Crea o actualiza un plato
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    decoded = jwt.decode(token, options={"verify_signature": False})
    restaurante_id = decoded.get("restaurant_id")

    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "precio_oferta": precio_oferta,
        "imagen_url": imagen_url,
        "categoria_id": categoria_id,
        "disponible": disponible,
        "destacado": destacado,
        "etiquetas": [e.strip() for e in etiquetas.split(",")] if etiquetas else [],
        "posicion": posicion,
        "restaurante_id": restaurante_id
    }

    if plato_id:
        resultado = update_dish(token, plato_id, payload)
    else:
        resultado = create_dish(token, payload)

    categorias = _sign_dish_images(list_dishes(token))

    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "categorias": categorias,
            "plato": None,
            "error": resultado.get("detalle") if "error" in resultado else None,
            "success": None if "error" in resultado else "Operación realizada correctamente",
            **get_template_context(request)
        }
    )


@router.post("/eliminar/{dish_id}", response_class=HTMLResponse)
def eliminar(request: Request, dish_id: str):
    """
    Elimina un plato
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    resultado = delete_dish(token, dish_id)
    categorias = _sign_dish_images(list_dishes(token))

    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "categorias": categorias,
            "plato": None,
            "error": resultado.get("detalle") if "error" in resultado else None,
            "success": None if "error" in resultado else "Plato eliminado correctamente",
            **get_template_context(request)
        }
    )


@router.post("/toggle_availability/{dish_id}", response_class=HTMLResponse)
def toggle(request: Request, dish_id: str):
    """
    Cambia disponibilidad de un plato
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    resultado = toggle_availability(token, dish_id)
    categorias = _sign_dish_images(list_dishes(token))

    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "categorias": categorias,
            "plato": None,
            "error": resultado.get("detalle") if "error" in resultado else None,
            "success": None if "error" in resultado else "Disponibilidad actualizada",
            **get_template_context(request)
        }
    )
