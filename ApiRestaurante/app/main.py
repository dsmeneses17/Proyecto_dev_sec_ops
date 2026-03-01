from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from limits import parse as parse_rate_limit
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import admin_category, admin_dish, admin_restaurant, analytics, auth, public_menu

# ---------------------------------------------------------------------------
# Rate limiter – 100 requests per minute per client IP  (RNF-04)
# ---------------------------------------------------------------------------
_storage = MemoryStorage()
_strategy = MovingWindowRateLimiter(_storage)
_rate = parse_rate_limit("100/minute")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests that exceed 100 req/min per client IP."""

    async def dispatch(self, request: Request, call_next):
        client_ip = (request.client.host if request.client else "127.0.0.1")
        key = f"rate_limit:{client_ip}"

        if not _strategy.hit(_rate, key):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded: 100 per 1 minute"},
            )
        return await call_next(request)


app = FastAPI()
app.add_middleware(RateLimitMiddleware)

# Incluye routers con prefijos claros
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_category.router, prefix="/api/v1/admin/categories")
app.include_router(admin_dish.router, prefix="/api/v1/admin/dishes", tags=["dishes"])
app.include_router(admin_restaurant.router, prefix="/api/v1/admin/restaurants")
app.include_router(public_menu.router)
app.include_router(analytics.router)

# Debug: imprime todas las rutas registradas
for route in app.routes:
    print(route.path, route.methods)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}
