from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from app.ui.templates import templates
from app.services.auth_service import register_owner_with_restaurant


router = APIRouter()


@router.get("/registro")
def show_register(request: Request):
    return templates.TemplateResponse("register_owner.html", {"request": request})


@router.post("/registro")
def submit_register(
    request: Request,
    nombre_completo: str = Form(...),
    email: str = Form(...),
    usuario: str = Form(...),
    password: str = Form(...),
    restaurant_nombre: str = Form(...),
    restaurant_slug: str = Form(...),
    restaurant_telefono: str | None = Form(None),
    restaurant_direccion: str | None = Form(None),
):
    payload = {
        "nombre_completo": nombre_completo,
        "email": email,
        "usuario": usuario,
        "password": password,
        "restaurant_nombre": restaurant_nombre,
        "restaurant_slug": restaurant_slug,
        "restaurant_telefono": restaurant_telefono,
        "restaurant_direccion": restaurant_direccion,
    }

    result = register_owner_with_restaurant(payload)
    if "error" in result:
        return templates.TemplateResponse(
            "register_owner.html",
            {"request": request, "error": result["error"]},
        )

    # After success, return to login.
    return RedirectResponse(url="/", status_code=303)
