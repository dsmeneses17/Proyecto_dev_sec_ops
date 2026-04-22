import logging

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from app.core.config import settings
from app.services.image_worker_pool import ImageWorkerPool
from app.services.storage import build_proxy_url, resolve_object_name

router = APIRouter(tags=["uploads"])
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = set(settings.IMAGE_ALLOWED_CONTENT_TYPES)
MAX_IMAGE_SIZE = settings.IMAGE_MAX_FILE_BYTES


def _get_image_pool(request: Request) -> ImageWorkerPool:
    pool = getattr(request.app.state, "image_worker_pool", None)
    if pool is None:
        raise HTTPException(status_code=503, detail="Worker pool no inicializado.")
    return pool


def _to_absolute_media_url(request: Request, image_ref: str) -> str:
    del request
    object_name = resolve_object_name(image_ref)
    if not object_name:
        return image_ref
    # Use relative paths to avoid mixed-content issues behind HTTPS load balancers.
    return build_proxy_url(object_name)


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    target: str = Query("general")
):
    token = request.cookies.get("access_token")
    rol = request.cookies.get("rol")
    user_id = request.cookies.get("user_id", "unknown")

    logger.info(
        "upload_image request received target=%s user_id=%s rol=%s token_present=%s content_type=%s filename=%s",
        target,
        user_id,
        rol,
        bool(token),
        file.content_type,
        file.filename,
    )

    if not token or rol != "admin":
        logger.warning(
            "upload_image rejected by auth: token_present=%s rol=%s expected_role=admin",
            bool(token),
            rol,
        )
        raise HTTPException(status_code=403, detail="No autorizado: token o rol invalido")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        logger.warning(
            "upload_image rejected by content type target=%s user_id=%s content_type=%s allowed=%s",
            target,
            user_id,
            file.content_type,
            sorted(ALLOWED_IMAGE_TYPES),
        )
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo JPEG, PNG o WebP."
        )

    image_content = await file.read(MAX_IMAGE_SIZE + 1)
    await file.close()

    if len(image_content) > MAX_IMAGE_SIZE:
        logger.warning(
            "upload_image rejected by size target=%s user_id=%s size=%s max=%s",
            target,
            user_id,
            len(image_content),
            MAX_IMAGE_SIZE,
        )
        raise HTTPException(status_code=400, detail="El archivo excede el máximo de 5MB.")

    pool = _get_image_pool(request)
    try:
        result = await pool.enqueue_and_wait(
            image_content=image_content,
            user_id=user_id,
            target=target,
            source_content_type=file.content_type,
        )

        urls = result.get("urls") or {}
        if isinstance(urls, dict):
            for key, value in list(urls.items()):
                if isinstance(value, str):
                    urls[key] = _to_absolute_media_url(request, value)

        if isinstance(result.get("url"), str):
            result["url"] = _to_absolute_media_url(request, result["url"])

        logger.info(
            "upload_image completed target=%s user_id=%s url=%s queue_size=%s",
            target,
            user_id,
            result.get("url"),
            result.get("worker_queue_size"),
        )
        return result
    except HTTPException:
        logger.exception("upload_image failed with HTTPException target=%s user_id=%s", target, user_id)
        raise
    except Exception:
        logger.exception("upload_image failed unexpectedly target=%s user_id=%s", target, user_id)
        raise
