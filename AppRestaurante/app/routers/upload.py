from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from app.core.config import settings
from app.services.image_worker_pool import ImageWorkerPool

router = APIRouter(tags=["uploads"])

ALLOWED_IMAGE_TYPES = set(settings.IMAGE_ALLOWED_CONTENT_TYPES)
MAX_IMAGE_SIZE = settings.IMAGE_MAX_FILE_BYTES


def _get_image_pool(request: Request) -> ImageWorkerPool:
    pool = getattr(request.app.state, "image_worker_pool", None)
    if pool is None:
        raise HTTPException(status_code=503, detail="Worker pool no inicializado.")
    return pool


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    target: str = Query("general")
):
    token = request.cookies.get("access_token")
    rol = request.cookies.get("rol")
    user_id = request.cookies.get("user_id", "unknown")

    if not token or rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo JPEG, PNG o WebP."
        )

    image_content = await file.read(MAX_IMAGE_SIZE + 1)
    await file.close()

    if len(image_content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el máximo de 5MB.")

    pool = _get_image_pool(request)
    return await pool.enqueue_and_wait(
        image_content=image_content,
        user_id=user_id,
        target=target,
        source_content_type=file.content_type,
    )
