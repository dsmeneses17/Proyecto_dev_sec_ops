import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from limits import parse as parse_rate_limit
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.security import decode_token
from app.routers import analytics as analytics_router
from app.routers import auth, category, dish, internal_image, public_menu, register_owner, restaurant, upload
from app.services.backend_auth import request_backend
from app.services.image_worker_pool import ImageProcessingConfig, ImageWorkerPool
from app.ui.templates import templates

from .utils.templates import get_template_context


def _register_shutdown_signal_handlers(shutdown_event: asyncio.Event):
    loop = asyncio.get_running_loop()
    signals = [signal.SIGTERM, signal.SIGINT]
    previous_handlers: dict[int, signal.Handlers] = {}

    def _handle_signal(signum: int):
        if not shutdown_event.is_set():
            loop.call_soon_threadsafe(shutdown_event.set)

    for current_signal in signals:
        try:
            loop.add_signal_handler(current_signal, _handle_signal, current_signal)
        except NotImplementedError:
            previous_handlers[current_signal] = signal.getsignal(current_signal)
            signal.signal(current_signal, lambda signum, frame: _handle_signal(signum))

    def _cleanup_handlers():
        for current_signal, previous_handler in previous_handlers.items():
            signal.signal(current_signal, previous_handler)

    return _cleanup_handlers


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    shutdown_event = asyncio.Event()
    cleanup_signal_handlers = _register_shutdown_signal_handlers(shutdown_event)

    image_pool = ImageWorkerPool(
        ImageProcessingConfig(
            workers=settings.IMAGE_WORKERS,
            queue_maxsize=settings.IMAGE_QUEUE_MAXSIZE,
            queue_put_timeout_sec=settings.IMAGE_QUEUE_PUT_TIMEOUT_SEC,
            shutdown_timeout_sec=settings.IMAGE_SHUTDOWN_TIMEOUT_SEC,
            max_image_size_bytes=settings.IMAGE_MAX_FILE_BYTES,
            allowed_image_types=settings.IMAGE_ALLOWED_CONTENT_TYPES,
            allowed_targets=settings.IMAGE_ALLOWED_TARGETS,
            variants={
                "thumbnail": (240, 240),
                "medium": (800, 800),
                "large": (1400, 1400),
            },
        )
    )
    await image_pool.start()

    app_instance.state.image_worker_pool = image_pool
    app_instance.state.shutdown_event = shutdown_event

    try:
        yield
    finally:
        cleanup_signal_handlers()
        await image_pool.shutdown()


app = FastAPI(lifespan=lifespan)

# ---------------------------------------------------------------------------
# Rate limiter – 100 requests per minute per client IP  (RNF-04)
# ---------------------------------------------------------------------------
_storage = MemoryStorage()
_strategy = MovingWindowRateLimiter(_storage)
_rate = parse_rate_limit("100/minute")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests that exceed 100 req/min per client IP."""

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"rate_limit:{client_ip}"

        if not _strategy.hit(_rate, key):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded: 100 per 1 minute"},
            )
        return await call_next(request)


app.add_middleware(RateLimitMiddleware)


# ---------------------------------------------------------------------------
# Security & performance headers  (RNF-09 Lighthouse best-practices)
# ---------------------------------------------------------------------------
class LighthouseHeadersMiddleware(BaseHTTPMiddleware):
    """Add headers that improve Lighthouse Performance / Best-Practices score."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Cache static assets for 1 day
        if request.url.path.startswith("/static"):
            response.headers["Cache-Control"] = "public, max-age=86400"
        # Security headers expected by Lighthouse best-practices
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        return response


app.add_middleware(LighthouseHeadersMiddleware)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Public paths that shouldn't require JWT cookies.
PUBLIC_PATHS = [
    "/static",
    "/favicon.ico",
    "/robots.txt",
    "/media",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/register-client",
    "/registro",
    "/menu",
]


def _is_public_path(request_path: str) -> bool:
    """Check if a path is public"""
    # Exact match for root
    if request_path == "/":
        return True
    # Prefix match for other paths
    if any(request_path.startswith(path + "/") or request_path == path for path in PUBLIC_PATHS if path != "/"):
        return True
    return False


# Plantillas HTML (shared)


@app.get("/robots.txt", response_class=FileResponse, include_in_schema=False)
def robots_txt():
    """Serve robots.txt for Lighthouse SEO audit (RNF-09)."""
    return FileResponse("app/static/robots.txt", media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
def mostrar_login(request: Request):
    # If the user is already authenticated, route to the appropriate dashboard.
    token = request.cookies.get("access_token")
    if token:
        rol = request.cookies.get("rol", "")
        if rol == "cliente":
            return RedirectResponse(url="/cliente", status_code=303)
        return RedirectResponse(url="/restaurants/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/cliente", response_class=HTMLResponse)
def cliente_dashboard(request: Request):
    """Dashboard for clients: shows all available restaurants to explore."""
    from app.services.menu_service import list_public_restaurants
    from app.services.storage import build_display_url

    restaurants = list_public_restaurants()
    # Sign logo URLs so images display correctly
    for r in restaurants:
        if r.get("logo_url"):
            r["logo_url"] = build_display_url(r["logo_url"])

    return templates.TemplateResponse(
        "cliente_dashboard.html",
        {**get_template_context(request), "restaurants": restaurants},
    )


@app.middleware("http")
async def enforce_https_middleware(request: Request, call_next):
    if not settings.ENFORCE_HTTPS_REDIRECT:
        return await call_next(request)

    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    is_https = request.url.scheme == "https" or forwarded_proto.split(",")[0].strip().lower() == "https"

    if not is_https:
        https_url = str(request.url.replace(scheme="https"))
        return RedirectResponse(url=https_url, status_code=307)

    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# cPUBLIC_PATHS = ["/", "/auth/login", "/auth/register"]


@app.get("/restaurant", response_class=HTMLResponse)
async def restaurant_dashboard(request: Request):
    context = get_template_context(request)
    return templates.TemplateResponse("restaurants/restaurant_form.html", {context})


@app.get("/restaurant_form", response_class=HTMLResponse)
async def restaurant_form(request: Request):
    token = request.cookies.get("access_token")
    restaurant_id = request.cookies.get("restaurant_id")
    _ = request.cookies.get("restaurant_slug")  # kept for future use
    _ = request.cookies.get("user_id")  # kept for future use
    context = get_template_context(request)
    if not token or not restaurant_id:
        # No autorizado → redirigir al login o dashboard
        return RedirectResponse(url="/", status_code=303)

    # Llamar a la API para obtener los datos del restaurante
    try:
        resp = request_backend(
            "GET",
            f"{settings.BACKEND_URL}/admin/restaurants/{restaurant_id}",
            user_token=token,
            timeout=10,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {"request": request, "error": f"No se pudo conectar a la API: {e}", "context": context},
        )

    if resp.status_code != 200:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {"error": f"Error {resp.status_code} al obtener datos", **get_template_context(request)},
        )

    restaurant_data = resp.json()  # JSON devuelto por la API
    # Si la API devuelve una lista, tomar el primer elemento
    restaurant = restaurant_data[0] if isinstance(restaurant_data, list) else restaurant_data

    return templates.TemplateResponse(
        "restaurants/restaurant_form.html", {"restaurant": restaurant, **get_template_context(request)}
    )


@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    if _is_public_path(request.url.path):
        return await call_next(request)

    accepts = (request.headers.get("accept") or "").lower()
    requested_with = (request.headers.get("x-requested-with") or "").lower()
    is_api_or_ajax = (
        request.url.path.startswith("/api/")
        or request.url.path.startswith("/uploads/")
        or "application/json" in accepts
        or requested_with == "xmlhttprequest"
    )

    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("access_token")

    if not token:
        if is_api_or_ajax:
            return JSONResponse(status_code=401, content={"detail": "No autenticado"})
        return RedirectResponse(url="/", status_code=303)

    try:
        payload = decode_token(token)
        request.state.user = payload
    except Exception:
        if is_api_or_ajax:
            response = JSONResponse(status_code=401, content={"detail": "Token invalido o expirado"})
            response.delete_cookie("access_token")
            response.delete_cookie("rol")
            response.delete_cookie("user_id")
            response.delete_cookie("restaurant_id")
            response.delete_cookie("restaurant_slug")
            return response

        # Token invalid/expired -> clear cookies so we don't loop and send to login
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.delete_cookie("access_token")
        redirect.delete_cookie("rol")
        redirect.delete_cookie("user_id")
        redirect.delete_cookie("restaurant_id")
        redirect.delete_cookie("restaurant_slug")
        return redirect

    return await call_next(request)


# Incluir routers de API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(restaurant.router, prefix="/restaurants", tags=["restaurantes"])
app.include_router(category.router, prefix="/categories", tags=["categorias"])
app.include_router(dish.router, prefix="/platos", tags=["platos"])
app.include_router(upload.router, prefix="/uploads", tags=["uploads"])
app.include_router(internal_image.router)
app.include_router(public_menu.router)
app.include_router(register_owner.router)
app.include_router(analytics_router.router)
