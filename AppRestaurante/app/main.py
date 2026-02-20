from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import public_menu
from.utils.templates import get_template_context
from app.core.config import settings




from app.routers import auth, restaurant, category, dish


from app.core.security import decode_token

app = FastAPI()





# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# PUBLIC_PATHS = [ "/api/v1/auth/login", "/api/v1/auth/register"]
PUBLIC_PATHS = ["/", "/static", "/favicon.ico"]
# Plantillas HTML
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})




#cPUBLIC_PATHS = ["/", "/auth/login", "/auth/register"]


@app.get("/restaurant", response_class=HTMLResponse)
async def restaurant_dashboard(request: Request):
    context = get_template_context(request)
    return templates.TemplateResponse("restaurants/restaurant_form.html", 
                                      { context })

@app.get("/restaurant_form", response_class=HTMLResponse)
async def restaurant_form(request: Request):
    token = request.cookies.get("access_token")
    restaurant_id = request.cookies.get("restaurant_id")
    restaurant_slug = request.cookies.get("restaurant_slug")
    user_id = request.cookies.get("user_id")
    context = get_template_context(request)
    if not token or not restaurant_id:
        # No autorizado → redirigir al login o dashboard
        return RedirectResponse(url="/", status_code=303)

    # Llamar a la API para obtener los datos del restaurante
    import requests
    try:
        resp = requests.get(
            f"{settings.BACKEND_URL}/admin/restaurants/{restaurant_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            {"request": request, 
             "error": f"No se pudo conectar a la API: {e}",
              "context": context}
        )

    if resp.status_code != 200:
        return templates.TemplateResponse(
            "restaurants/restaurant_form.html",
            { 
             "error": f"Error {resp.status_code} al obtener datos",
              **get_template_context(request)}
        )

    restaurant_data = resp.json()  # JSON devuelto por la API
    # Si la API devuelve una lista, tomar el primer elemento
    restaurant = restaurant_data[0] if isinstance(restaurant_data, list) else restaurant_data

    return templates.TemplateResponse(
        "restaurants/restaurant_form.html",
        { "restaurant": restaurant, **get_template_context(request)}
    )



@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    
    if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        #breakpoint()
        payload = decode_token(token)
        #request.state.user = payload.get("sub")
        request.state.user = payload
    except Exception:
        return RedirectResponse(url="/", status_code=303)

    return await call_next(request)

# Incluir routers de API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(restaurant.router, prefix="/restaurants", tags=["restaurantes"])
app.include_router(category.router, prefix="/categories", tags=["categorias"])
app.include_router(dish.router, prefix="/platos", tags=["platos"])  
app.include_router(public_menu.router)






# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from app.routers import auth
# from app.core.security import decode_token
# from app.routers import restaurant  
# from fastapi.staticfiles import StaticFiles

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="app/static"), name="static")



# # Plantillas HTML
# templates = Jinja2Templates(directory="app/templates")

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# # Rutas públicas que no requieren autenticación
# PUBLIC_PATHS = ["/", "/auth/login", "/auth/register"]

# @app.get("/restaurant", response_class=HTMLResponse)
# async def restaurant_dashboard(request: Request):
#     return templates.TemplateResponse("restaurant.html", {"request": request})

# @app.get("/restaurant_form.html", response_class=HTMLResponse)
# async def restaurant_form(request: Request):
#     return templates.TemplateResponse("restaurants/restaurant_form.html", {"request": request})


# @app.middleware("http")
# async def jwt_middleware(request: Request, call_next):
#     # Rutas públicas
#     if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
#         return await call_next(request)

#     # 1. Buscar token en header
#     auth_header = request.headers.get("Authorization")
#     token = None

#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#     else:
#         # 2. Buscar token en cookies
#         token = request.cookies.get("token")

#     if not token:
#         return RedirectResponse(url="/login", status_code=303)

#     try:
#         payload = decode_token(token)
#         request.state.user = payload.get("sub")
#     except Exception:
#         return RedirectResponse(url="/login", status_code=303)

#     return await call_next(request)

# # @app.middleware("http")
# # async def jwt_middleware(request: Request, call_next):
# #     # Si la ruta es pública, no validamos token
# #     if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
# #         return await call_next(request)

# #     # Extraer header Authorization
# #     auth_header = request.headers.get("Authorization")
# #     if not auth_header or not auth_header.startswith("Bearer "):
# #         return JSONResponse(status_code=401, content={"detail": "Token requerido"})

# #     token = auth_header.split(" ")[1]

# #     try:
# #         payload = decode_token(token)
# #         request.state.user = payload.get("sub")  # Guardamos el usuario en el request
# #     except Exception:
# #         return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})

# #     return await call_next(request)

# # Incluir routers
# app.include_router(auth.router)

# ##app.include_router(restaurant.router)
# app.include_router(restaurant.router, prefix="", tags=["restaurant"])



