"""Service for handling QR color updates."""

import logging
import re

from app.core.security import decode_token
from app.services.menu_service import get_public_menu
from app.services.restaurant_service import update_restaurant_colors

HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def process_qr_color_update(token: str, slug: str, qr_color_fg: str, qr_color_bg: str) -> dict:
    """
    Process QR color update request.

    Returns dict with either:
        {"success": True, "message": "..."} on success
        {"error": True, "status_code": int, "detail": "..."} on failure
    """
    # Verify token
    try:
        payload = decode_token(token)
        if not payload or "restaurant_id" not in payload:
            return {"error": True, "status_code": 403, "detail": "No autorizado"}
    except Exception:
        return {"error": True, "status_code": 403, "detail": "Token inválido"}

    # Get menu and verify restaurant
    menu = get_public_menu(slug)
    if not menu:
        return {"error": True, "status_code": 404, "detail": "Restaurante no encontrado"}

    if str(menu.restaurant.id) != str(payload["restaurant_id"]):
        return {"error": True, "status_code": 403, "detail": "No eres propietario de este restaurante"}

    # Validate colors
    if not HEX_PATTERN.match(qr_color_fg):
        return {"error": True, "status_code": 400, "detail": "Color QR inválido"}
    if not HEX_PATTERN.match(qr_color_bg):
        return {"error": True, "status_code": 400, "detail": "Color fondo inválido"}

    # Call backend API
    try:
        result = update_restaurant_colors(token, menu.restaurant.id, qr_color_fg, qr_color_bg)

        if "error" in result:
            return {
                "error": True,
                "status_code": 400,
                "detail": result.get("detalle", "Error al actualizar colores"),
            }

        return {"success": True, "message": "Colores actualizados correctamente"}
    except Exception as e:
        logging.error("Color update error: %s", e)
        return {"error": True, "status_code": 500, "detail": str(e)}
