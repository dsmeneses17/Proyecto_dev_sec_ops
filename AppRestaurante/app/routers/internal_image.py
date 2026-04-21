"""Internal image endpoints for proxying private object-storage images."""

import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from botocore.exceptions import BotoCoreError, ClientError

from app.services.storage import build_display_url, read_object_from_storage

router = APIRouter(tags=["internal-image"])
logger = logging.getLogger(__name__)


@router.get("/api/internal/signed-image-url")
async def get_signed_image_url(
    object_name: str = Query(..., description="Object name or URL to sign")
):
    """
    Convert object_name or URL to app proxy URL for display.
    Used by frontend templates to avoid signed URLs in clients.
    
    Args:
        object_name: e.g. "uploads/user123/logo/abc.webp" or full URL
        
    Returns:
        App media proxy URL
    """
    if not object_name:
        raise HTTPException(status_code=400, detail="object_name is required")
    
    logger.debug("Signing image URL object_name=%s", object_name)
    
    try:
        proxy_url = build_display_url(object_name, expires_in_seconds=3600)
        logger.info("Image proxy URL generated successfully")
        return {"url": proxy_url}
    except Exception as exc:
        logger.exception("Failed to build proxy URL object_name=%s", object_name)
        raise HTTPException(status_code=500, detail="No se pudo generar URL de imagen") from exc


@router.get("/media/{object_name:path}", include_in_schema=False)
async def proxy_media(object_name: str):
    """Proxy private object-storage images through the app without signed URLs."""
    if not object_name:
        raise HTTPException(status_code=400, detail="Ruta de imagen invalida")

    try:
        content, content_type, cache_control = read_object_from_storage(object_name)
    except FileNotFoundError as exc:
        logger.warning("Media object not found object_name=%s", object_name)
        raise HTTPException(status_code=404, detail="Imagen no encontrada") from exc
    except (BotoCoreError, ClientError):
        logger.exception("S3 media proxy failed object_name=%s", object_name)
        raise HTTPException(status_code=502, detail="Error leyendo imagen desde storage")
    except Exception:
        logger.exception("Media proxy failed object_name=%s", object_name)
        raise HTTPException(status_code=500, detail="Error interno al leer imagen")

    headers = {}
    if cache_control:
        headers["Cache-Control"] = cache_control
    else:
        headers["Cache-Control"] = "public, max-age=3600"

    return Response(content=content, media_type=content_type, headers=headers)
