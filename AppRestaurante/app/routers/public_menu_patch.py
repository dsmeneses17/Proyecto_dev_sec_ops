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
