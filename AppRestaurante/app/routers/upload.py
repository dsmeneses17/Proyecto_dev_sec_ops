from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from PIL import Image, UnidentifiedImageError
from app.services.storage import StorageConfigurationError, upload_bytes_to_object_storage


router = APIRouter(tags=["uploads"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_TARGETS = {"logo", "dish", "general"}
IMAGE_VARIANTS = {
    "thumbnail": (240, 240),
    "medium": (800, 800),
    "large": (1400, 1400),
}
OUTPUT_FORMAT = "WEBP"
OUTPUT_EXTENSION = ".webp"
OUTPUT_QUALITY = 82


def _normalize_image(content: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(content))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        return image
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="No se pudo procesar el archivo de imagen.") from exc


def _render_variant(base_image: Image.Image, max_size: tuple[int, int]) -> bytes:
    variant = base_image.copy()
    variant.thumbnail(max_size, Image.Resampling.LANCZOS)

    save_kwargs = {
        "format": OUTPUT_FORMAT,
        "quality": OUTPUT_QUALITY,
        "method": 6,
    }

    if variant.mode == "RGBA":
        save_kwargs["lossless"] = False

    buffer = BytesIO()
    variant.save(buffer, **save_kwargs)
    return buffer.getvalue()


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

    safe_target = target if target in ALLOWED_TARGETS else "general"
    source_image = _normalize_image(image_content)

    image_id = uuid4().hex
    urls = {}
    for variant_name, variant_size in IMAGE_VARIANTS.items():
        filename = f"{image_id}_{variant_name}{OUTPUT_EXTENSION}"
        object_name = f"uploads/{user_id}/{safe_target}/{filename}"
        variant_content = _render_variant(source_image, variant_size)
        try:
            urls[variant_name] = upload_bytes_to_object_storage(
                content=variant_content,
                object_name=object_name,
                content_type="image/webp",
            )
        except StorageConfigurationError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "url": urls["medium"],
        "urls": urls,
        "size": len(image_content),
        "content_type": file.content_type,
    }
