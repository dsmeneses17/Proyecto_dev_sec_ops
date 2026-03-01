import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from app.services.storage import StorageConfigurationError, upload_bytes_to_object_storage

OUTPUT_FORMAT = "WEBP"
OUTPUT_EXTENSION = ".webp"
OUTPUT_CONTENT_TYPE = "image/webp"
OUTPUT_QUALITY = 82


@dataclass
class ImageProcessingConfig:
    workers: int
    queue_maxsize: int
    queue_put_timeout_sec: float
    shutdown_timeout_sec: float
    max_image_size_bytes: int
    allowed_image_types: tuple[str, ...]
    allowed_targets: tuple[str, ...]
    variants: dict[str, tuple[int, int]]


@dataclass
class ImageProcessingJob:
    image_content: bytes
    user_id: str
    target: str
    source_content_type: str
    result_future: asyncio.Future


def _normalize_image(content: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(content))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        return image
    except UnidentifiedImageError as exc:
        raise ValueError("No se pudo procesar el archivo de imagen.") from exc


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


def _process_image_variants_cpu(
    image_content: bytes,
    image_variants: dict[str, tuple[int, int]],
) -> dict[str, bytes]:
    source_image = _normalize_image(image_content)
    variants: dict[str, bytes] = {}
    for variant_name, variant_size in image_variants.items():
        variants[variant_name] = _render_variant(source_image, variant_size)
    return variants


class ImageWorkerPool:
    def __init__(self, config: ImageProcessingConfig):
        self.config = config
        self.queue: asyncio.Queue[ImageProcessingJob | None] = asyncio.Queue(maxsize=config.queue_maxsize)
        self.executor = ProcessPoolExecutor(max_workers=config.workers)
        self.worker_tasks: list[asyncio.Task] = []
        self._accepting_jobs = False

    async def start(self):
        if self.worker_tasks:
            return

        self._accepting_jobs = True
        for index in range(self.config.workers):
            task = asyncio.create_task(self._worker_loop(index), name=f"image-worker-{index}")
            self.worker_tasks.append(task)

    async def shutdown(self):
        self._accepting_jobs = False

        try:
            await asyncio.wait_for(self.queue.join(), timeout=self.config.shutdown_timeout_sec)
        except TimeoutError:
            pass

        for _ in self.worker_tasks:
            await self.queue.put(None)

        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            self.worker_tasks.clear()

        self.executor.shutdown(wait=True)

    async def enqueue_and_wait(
        self,
        *,
        image_content: bytes,
        user_id: str,
        target: str,
        source_content_type: str,
    ) -> dict[str, Any]:
        if not self._accepting_jobs:
            raise HTTPException(status_code=503, detail="Servicio temporalmente no disponible.")

        safe_target = target if target in self.config.allowed_targets else "general"
        loop = asyncio.get_running_loop()
        result_future = loop.create_future()
        job = ImageProcessingJob(
            image_content=image_content,
            user_id=user_id,
            target=safe_target,
            source_content_type=source_content_type,
            result_future=result_future,
        )

        try:
            await asyncio.wait_for(self.queue.put(job), timeout=self.config.queue_put_timeout_sec)
        except TimeoutError as exc:
            raise HTTPException(status_code=503, detail="La cola de procesamiento está llena.") from exc

        return await result_future

    async def _worker_loop(self, worker_index: int):
        while True:
            job = await self.queue.get()
            if job is None:
                self.queue.task_done()
                break

            try:
                result = await self._process_job(job)
                if not job.result_future.done():
                    job.result_future.set_result(result)
            except Exception as exc:
                if not job.result_future.done():
                    job.result_future.set_exception(exc)
            finally:
                self.queue.task_done()

    async def _process_job(self, job: ImageProcessingJob) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        image_id = uuid4().hex
        try:
            processed_variants = await loop.run_in_executor(
                self.executor,
                _process_image_variants_cpu,
                job.image_content,
                self.config.variants,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        urls: dict[str, str] = {}
        for variant_name, variant_content in processed_variants.items():
            filename = f"{image_id}_{variant_name}{OUTPUT_EXTENSION}"
            object_name = f"uploads/{job.user_id}/{job.target}/{filename}"
            try:
                urls[variant_name] = await asyncio.to_thread(
                    upload_bytes_to_object_storage,
                    variant_content,
                    object_name,
                    OUTPUT_CONTENT_TYPE,
                )
            except StorageConfigurationError as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            except RuntimeError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc

        return {
            "url": urls.get("medium") or next(iter(urls.values())),
            "urls": urls,
            "size": len(job.image_content),
            "content_type": job.source_content_type,
            "worker_queue_size": self.queue.qsize(),
        }
