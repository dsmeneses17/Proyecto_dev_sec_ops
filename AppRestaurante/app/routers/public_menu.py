from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.services.menu_service import get_public_menu, list_public_restaurants

import qrcode
import qrcode.image.svg
import io
import base64
from fastapi.responses import Response

router = APIRouter()


def _build_public_menu_url(request: Request, slug: str) -> str:
    return f"{str(request.base_url).rstrip('/')}/menu/{slug}"


def _generate_qr_png_bytes(content: str, fill_color: str = "#000000", back_color: str = "#FFFFFF") -> bytes:
    """Generate QR code as PNG bytes with custom colors.
    
    Args:
        content: The data to encode
        fill_color: Foreground color (hex code, e.g., "#000000")
        back_color: Background color (hex code, e.g., "#FFFFFF")
    """
    # Convert hex colors to RGB tuples
    fill_rgb = tuple(int(fill_color[i:i+2], 16) for i in (1, 3, 5))
    back_rgb = tuple(int(back_color[i:i+2], 16) for i in (1, 3, 5))
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fill_rgb, back_color=back_rgb)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _generate_qr_svg_bytes(content: str) -> bytes:
    qr = qrcode.make(content, image_factory=qrcode.image.svg.SvgPathImage)
    buffer = io.BytesIO()
    qr.save(buffer)
    return buffer.getvalue()


@router.get("/menu", response_class=HTMLResponse)
def menu_index(request: Request, slug: str | None = None):
    """Public entrypoint to access menus without logging in.

    - If `?slug=...` is provided, redirect to `/menu/{slug}`.
    - Else if a `restaurant_slug` cookie exists, redirect to that menu.
    - Otherwise render a small form to enter the slug.
    """

    candidate = (slug or "").strip() or (request.cookies.get("restaurant_slug") or "").strip()
    if candidate:
        return RedirectResponse(url=f"/menu/{candidate}", status_code=303)

    restaurants = list_public_restaurants()

    return templates.TemplateResponse(
        "public/menu_index.html",
        {
            "request": request,
            "restaurants": restaurants,
            "selected_slug": (slug or "").strip(),
        }
    )


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

    menu = get_public_menu(slug)
    
    if not menu:
        return templates.TemplateResponse(
            "public/menu_not_found.html",
            {"request": request}
        )
    
    url_publica = _build_public_menu_url(request, slug)
    
    # Get QR colors from menu data
    qr_color_fg = menu.restaurant.qr_color_fg if hasattr(menu.restaurant, 'qr_color_fg') else "#000000"
    qr_color_bg = menu.restaurant.qr_color_bg if hasattr(menu.restaurant, 'qr_color_bg') else "#FFFFFF"
    
    png_bytes = _generate_qr_png_bytes(url_publica, fill_color=qr_color_fg, back_color=qr_color_bg)
    img_str = base64.b64encode(png_bytes).decode()

    return templates.TemplateResponse(
        "public/qr.html",
        {
            "request": request,
            "slug": slug,
            "qr_base64": img_str,
            "url_publica": url_publica,
            "qr_png_download_url": f"/menu/{slug}/qr.png",
            "qr_svg_download_url": f"/menu/{slug}/qr.svg",
        }
    )


@router.get("/menu/{slug}/qr.png")
def exportar_qr_png(request: Request, slug: str):
    menu = get_public_menu(slug)
    
    if not menu:
        return templates.TemplateResponse(
            "public/menu_not_found.html",
            {"request": request}
        )
    
    url_publica = _build_public_menu_url(request, slug)
    
    # Get QR colors from menu data
    qr_color_fg = menu.restaurant.qr_color_fg if hasattr(menu.restaurant, 'qr_color_fg') else "#000000"
    qr_color_bg = menu.restaurant.qr_color_bg if hasattr(menu.restaurant, 'qr_color_bg') else "#FFFFFF"
    
    png_bytes = _generate_qr_png_bytes(url_publica, fill_color=qr_color_fg, back_color=qr_color_bg)
    safe_slug = slug.replace(" ", "-")
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="menu-{safe_slug}-qr.png"'},
    )


@router.get("/menu/{slug}/qr.svg")
def exportar_qr_svg(request: Request, slug: str):
    url_publica = _build_public_menu_url(request, slug)
    svg_bytes = _generate_qr_svg_bytes(url_publica)
    safe_slug = slug.replace(" ", "-")
    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="menu-{safe_slug}-qr.svg"'},
    )