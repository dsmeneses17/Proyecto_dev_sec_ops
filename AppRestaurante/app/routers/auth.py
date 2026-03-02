from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.services import auth_service
from app.ui.templates import templates

router = APIRouter()


def _set_auth_cookie(response: RedirectResponse, key: str, value: str, httponly: bool = False):
    response.set_cookie(
        key,
        value,
        httponly=httponly,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )



@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("rol")
    response.delete_cookie("user_id")
    response.delete_cookie("restaurant_id")
    response.delete_cookie("restaurant_slug")
    return response

@router.get("/login")
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-client")
def mostrar_registro_cliente(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register-client")
def procesar_registro_cliente(
    request: Request,
    nombre_completo: str = Form(...),
    usuario: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    resultado = auth_service.register_client(
        nombre_completo=nombre_completo,
        usuario=usuario,
        email=email,
        password=password,
    )

    if "error" in resultado:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": resultado["error"]},
        )

    # Registro exitoso → redirigir al login con mensaje de éxito
    return RedirectResponse(url="/api/v1/auth/login?registered=1", status_code=303)

@router.post("/login")
def procesar_login(request: Request, usuario: str = Form(...), password: str = Form(...)):
    resultado = auth_service.autenticar_usuario(usuario, password)

    if "error" in resultado:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": resultado["error"]}
        )

    token = resultado["token"]
    rol = resultado["rol"]
    restaurant_id = resultado["restaurant_id"]
    restaurant_slug = resultado["restaurant_slug"]
    user_id = resultado.get("user_id")
    #breakpoint()
    #Admin con restaurante registrado → editar restaurante
    if rol == "admin":
        redirect = RedirectResponse(url="/restaurants", status_code=303)
        _set_auth_cookie(redirect, "access_token", token, httponly=True)
        _set_auth_cookie(redirect, "rol", rol)
        _set_auth_cookie(redirect, "user_id", str(user_id))
        _set_auth_cookie(redirect, "restaurant_id", str(restaurant_id))
        _set_auth_cookie(redirect, "restaurant_slug", str(restaurant_slug))
        return redirect



    # Cliente → client dashboard with all restaurants
    if rol == "cliente":
        redirect = RedirectResponse(url="/cliente", status_code=303)
        _set_auth_cookie(redirect, "access_token", token, httponly=True)
        _set_auth_cookie(redirect, "rol", rol)
        _set_auth_cookie(redirect, "user_id", str(user_id))
        _set_auth_cookie(redirect, "restaurant_id", str(restaurant_id))
        _set_auth_cookie(redirect, "restaurant_slug", str(restaurant_slug))

        return redirect

    # Otros roles
    redirect = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(redirect, "access_token", token, httponly=True)
    _set_auth_cookie(redirect, "rol", rol)
    _set_auth_cookie(redirect, "user_id", str(user_id))
    _set_auth_cookie(redirect, "restaurant_id", str(restaurant_id))
    _set_auth_cookie(redirect, "restaurant_slug", str(restaurant_slug))
    return redirect

