# app/routers/dish.py
from types import SimpleNamespace

import jwt
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.dish_service import create_dish, delete_dish, get_dish, list_dishes, toggle_availability, update_dish
from app.services.storage import build_display_url
from app.ui.templates import templates
from app.utils.templates import get_template_context

router = APIRouter(tags=["platos"])

def _safe_cookie_value(value: str | None):
    if value in [None, "", "None", "null"]:
        return None
    return value


def _sign_dish_images(categorias):
    if not isinstance(categorias, list):
        return categorias

    for categoria in categorias:
        platos = categoria.get("platos", []) if isinstance(categoria, dict) else []
        for plato in platos:
            if isinstance(plato, dict) and plato.get("imagen_url"):
                plato["imagen_url"] = build_display_url(plato["imagen_url"])
    return categorias


def _parse_tags(checkbox_tags: list[str] | None, manual_tags: str | None) -> list[str]:
    candidates: list[str] = []

    if checkbox_tags:
        candidates.extend(checkbox_tags)

    if manual_tags:
        candidates.append(manual_tags)

    if not candidates:
        return []

    parsed: list[str] = []
    for item in candidates:
        parts = str(item).split(",")
        for part in parts:
            normalized = part.strip().lower()
            if not normalized:
                continue
            parsed.append(normalized)

    unique_tags = list(dict.fromkeys(parsed))
    if len(unique_tags) > 10:
        raise HTTPException(status_code=400, detail="Máximo 10 etiquetas por plato")

    return unique_tags


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
    descripcion: str | None = Form(None),
    precio: float = Form(...),
    precio_oferta: float | None = Form(None),
    imagen_url: str | None = Form(None),
    categoria_id: str = Form(...),
    disponible: bool | None = Form(True),
    destacado: bool | None = Form(False),
    etiquetas: list[str] | None = Form(None),
    etiquetas_manual: str | None = Form(None),
    posicion: int | None = Form(None),
    plato_id: str | None = Form(None)
):
    """
    Crea o actualiza un plato
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    restaurante_id = _safe_cookie_value(request.cookies.get("restaurant_id"))
    if not restaurante_id:
        decoded = jwt.decode(token, options={"verify_signature": False})
        restaurante_id = decoded.get("restaurant_id")

    if not restaurante_id:
        categorias = _sign_dish_images(list_dishes(token))
        return templates.TemplateResponse(
            "dish_form.html",
            {
                "request": request,
                "categorias": categorias,
                "plato": None,
                "error": "No hay restaurante activo asociado. Guarda el restaurante antes de crear platos.",
                "success": None,
                **get_template_context(request),
            },
        )

    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "precio_oferta": precio_oferta,
        "imagen_url": imagen_url,
        "categoria_id": categoria_id,
        "disponible": disponible,
        "destacado": destacado,
        "etiquetas": _parse_tags(etiquetas, etiquetas_manual),
        "posicion": posicion,
        "restaurante_id": restaurante_id
    }

    if plato_id:
        resultado = update_dish(token, plato_id, payload)
    else:
        resultado = create_dish(token, payload)

    if "error" not in resultado:
        return RedirectResponse(url="/platos", status_code=303)

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
    if "error" not in resultado:
        return RedirectResponse(url="/platos", status_code=303)

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
            "success": "Disponibilidad actualizada" if "error" not in resultado else None,
            **get_template_context(request)
        }
    )
