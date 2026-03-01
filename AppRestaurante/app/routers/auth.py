from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.ui.templates import templates
from app.services import auth_service
from app.core.config import settings

router = APIRouter()



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
        redirect.set_cookie("access_token", token, httponly=True, secure=False, path="/")
        redirect.set_cookie("rol", rol)
        redirect.set_cookie("user_id", str(user_id))
        redirect.set_cookie("restaurant_id", str(restaurant_id))
        redirect.set_cookie("restaurant_slug", str(restaurant_slug))
        return redirect

   

    # Cliente → menú público
    if rol == "cliente":
        redirect = RedirectResponse(url="/menu", status_code=303)
        redirect.set_cookie("access_token", token, httponly=True, secure=False, path="/")
        redirect.set_cookie("rol", rol)
        redirect.set_cookie("user_id", str(user_id))
        redirect.set_cookie("restaurant_id", str(restaurant_id))
        redirect.set_cookie("restaurant_slug", str(restaurant_slug))
        
        return redirect

    # Otros roles 
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie("access_token", token, httponly=True, secure=True)
    redirect.set_cookie("rol", rol)
    redirect.set_cookie("user_id", str(user_id))
    redirect.set_cookie("restaurant_id", str(restaurant_id))
    redirect.set_cookie("restaurant_slug", str(restaurant_slug))
    return redirect

