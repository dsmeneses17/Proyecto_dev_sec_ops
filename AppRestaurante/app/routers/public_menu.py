from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from fastapi.responses import HTMLResponse
from app.services.menu_service import get_public_menu

import qrcode
import io
import base64
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/menu/{slug}", response_class=HTMLResponse)
def ver_menu(request: Request, slug: str):

    menu = get_public_menu(slug)

    if not menu:
        return templates.TemplateResponse(
            "public/menu_not_found.html",
            {"request": request}
        )

    return templates.TemplateResponse(
        "public/menu_public.html",
        {
            "request": request,
            "menu": menu
        }
    )

@router.get("/menu/{slug}/qr", response_class=HTMLResponse)
def generar_qr(request: Request, slug: str):

    url_publica = f"{request.base_url}menu/{slug}"

    qr = qrcode.make(url_publica)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return templates.TemplateResponse(
        "public/qr.html",
        {
            "request": request,
            "slug": slug,
            "qr_base64": img_str,
            "url_publica": url_publica
        }
    )