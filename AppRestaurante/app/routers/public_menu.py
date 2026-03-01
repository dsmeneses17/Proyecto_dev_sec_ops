from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.services.menu_service import get_public_menu, list_public_restaurants
from pydantic import BaseModel

import qrcode
import qrcode.image.svg
import io
import base64
from fastapi.responses import Response

router = APIRouter()


class QRColorUpdate(BaseModel):
    qr_color_fg: str
    qr_color_bg: str


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

    # Check if user is owner of this restaurant
    token = request.cookies.get("access_token")
    is_owner = False
    if token:
        try:
            from app.core.security import decode_token
            payload = decode_token(token)
            if payload and "restaurant_id" in payload:
                is_owner = str(menu.restaurant.id) == str(payload["restaurant_id"])
        except:
            pass

    return templates.TemplateResponse(
        "public/qr.html",
        {
            "request": request,
            "slug": slug,
            "qr_base64": img_str,
            "url_publica": url_publica,
            "qr_png_download_url": f"/menu/{slug}/qr.png",
            "qr_svg_download_url": f"/menu/{slug}/qr.svg",
            "qr_color_fg": qr_color_fg,
            "qr_color_bg": qr_color_bg,
            "is_owner": is_owner,
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



@router.post("/qr-colors/{slug}")
async def update_qr_colors(request: Request, slug: str):
    """
    Update QR colors for a restaurant
    Only restaurant owners can update their QR colors
    """
    # Get token from cookie or Authorization header
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    # Verify ownership
    try:
        from app.core.security import decode_token
        payload = decode_token(token)
        if not payload or "restaurant_id" not in payload:
            raise HTTPException(status_code=403, detail="No autorizado")
    except Exception:
        raise HTTPException(status_code=403, detail="Token inválido")

    # Get menu and verify restaurant
    menu = get_public_menu(slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if str(menu.restaurant.id) != str(payload["restaurant_id"]):
        raise HTTPException(status_code=403, detail="No eres propietario de este restaurante")

    # Parse JSON body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Validate colors format (hex #RRGGBB)
    import re
    hex_pattern = r"^#[0-9A-Fa-f]{6}$"
    
    qr_color_fg = body.get("qr_color_fg", "#000000")
    qr_color_bg = body.get("qr_color_bg", "#FFFFFF")

    if not re.match(hex_pattern, qr_color_fg):
        raise HTTPException(status_code=400, detail="Color QR inválido")
    if not re.match(hex_pattern, qr_color_bg):
        raise HTTPException(status_code=400, detail="Color fondo inválido")

    # Update restaurant colors via API
    try:
        from app.services.restaurant_service import update_restaurant_colors
        result = update_restaurant_colors(token, menu.restaurant.id, qr_color_fg, qr_color_bg)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result.get("detalle", "Error al actualizar colores"))

        return {"success": True, "message": "Colores actualizados correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Color update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
