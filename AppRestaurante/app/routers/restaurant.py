import json

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.core.config import settings
from app.models.restaurant_model import RestaurantCreate, RestaurantOut
from app.services.restaurant_service import (
    create_or_update_restaurant,
    delete_restaurant,
    get_restaurant_by_id,
)
from app.services.storage import build_display_url
from app.ui.templates import templates
from app.utils.templates import get_template_context

router = APIRouter()


def _safe_restaurant_cookie_value(value: str | None):
    if value in ["None", "", None]:
        return None
    return value


def _parse_horarios(raw_horarios: str):
    try:
        parsed = json.loads(raw_horarios)
        if isinstance(parsed, dict):
            return parsed
        if parsed in [None, "", []]:
            return {}
        return {"raw": str(parsed)}
    except Exception:
        return {}


def _prepare_restaurant_for_ui(restaurant_data: dict | None):
    if not isinstance(restaurant_data, dict):
        return restaurant_data

    if restaurant_data.get("logo"):
        restaurant_data["logo"] = build_display_url(restaurant_data["logo"])
    return restaurant_data


@router.get("/")
def mostrar_dashboard_restaurante(request: Request):
    token = request.cookies.get("access_token")
    rol = request.cookies.get("rol")
    restaurant_id = _safe_restaurant_cookie_value(request.cookies.get("restaurant_id"))

    if not token or rol != "admin":
        return RedirectResponse(url="/", status_code=303)

    if not restaurant_id:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {**get_template_context(request)},
        )

    resultado = get_restaurant_by_id(token, restaurant_id)

    if isinstance(resultado, dict) and resultado.get("error"):
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {"error": resultado.get("detalle", "No fue posible cargar restaurante"), **get_template_context(request)},
        )

    if resultado is None:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {**get_template_context(request)},
        )

    restaurant_data = _prepare_restaurant_for_ui(resultado)

    return templates.TemplateResponse(
        "restaurants/restaurant.html",
        {"restaurant": restaurant_data, **get_template_context(request)},
    )


@router.get("/restaurant_form", response_class=HTMLResponse)
def restaurant_form(request: Request):
    token = request.cookies.get("access_token")
    rol = request.cookies.get("rol")
    restaurant_id = _safe_restaurant_cookie_value(request.cookies.get("restaurant_id"))

    if not token or rol != "admin":
        return RedirectResponse(url="/", status_code=303)

    if not restaurant_id:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {**get_template_context(request)},
        )

    resultado = get_restaurant_by_id(token, restaurant_id)
    if isinstance(resultado, dict) and resultado.get("error"):
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {"error": resultado.get("detalle", "No fue posible cargar restaurante"), **get_template_context(request)},
        )

    restaurant_data = _prepare_restaurant_for_ui(resultado)

    return templates.TemplateResponse(
        "restaurants/restaurant_form.html",
        {"restaurant": restaurant_data, **get_template_context(request)},
    )


@router.post("/restaurant", response_model=RestaurantOut)
def create_restaurant(
    request: Request,
    response: Response,
    nombre: str = Form(...),
    slug: str = Form(...),
    logo: str = Form(""),
    descripcion: str = Form(None),
    telefono: str = Form(None),
    direccion: str = Form(None),
    horarios: str = Form("{}"),
):
    token = request.cookies.get("access_token")
    restaurant_id = _safe_restaurant_cookie_value(request.cookies.get("restaurant_id"))
    if not token:
        raise HTTPException(status_code=200, detail="Token requerido")

    logo = (logo or "").strip()
    if not logo:
        raise HTTPException(status_code=400, detail="Debe cargar el logo del restaurante")

    horarios_dict = _parse_horarios(horarios)

    try:
        restaurant = RestaurantCreate(
            id=restaurant_id,
            nombre=nombre,
            slug=slug,
            logo=logo,
            descripcion=descripcion,
            telefono=telefono,
            direccion=direccion,
            horarios=horarios_dict,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resultado = create_or_update_restaurant(restaurant, token)
    if "error" in resultado:
        raise HTTPException(status_code=200, detail=resultado)

    restaurant_id_result = resultado.get("id")
    restaurant_slug_result = resultado.get("slug")

    if restaurant_id_result:
        response.set_cookie(
            "restaurant_id",
            str(restaurant_id_result),
            path="/",
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
    if restaurant_slug_result:
        response.set_cookie(
            "restaurant_slug",
            str(restaurant_slug_result),
            path="/",
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

    return resultado


@router.post("/restaurant/delete")
def eliminar_restaurante(request: Request):
    token = request.cookies.get("access_token")
    restaurant_id = _safe_restaurant_cookie_value(request.cookies.get("restaurant_id"))

    if not token or not restaurant_id:
        return RedirectResponse(url="/restaurants/restaurant_form", status_code=303)

    resultado = delete_restaurant(token, restaurant_id)
    if isinstance(resultado, dict) and resultado.get("error"):
        raise HTTPException(status_code=400, detail=resultado.get("detalle", "No se pudo eliminar el restaurante"))

    redirect = RedirectResponse(url="/restaurants/restaurant_form", status_code=303)
    redirect.delete_cookie("restaurant_id")
    redirect.delete_cookie("restaurant_slug")
    return redirect


@router.post("/send")
def send_data(data: dict):
    return create_or_update_restaurant(data)
