from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.utils.templates import get_template_context
import jwt
from typing import Optional
from types import SimpleNamespace
from app.services.categoria_service import (
    list_categorias,
    create_categoria,
    update_categoria,
    delete_categoria,
    get_categoria,
    reorder_categorias
)

router = APIRouter(tags=["categorias"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def listar(request: Request):
    token = request.cookies.get("access_token")  # ❌ Leer cookie exacta
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    categorias = list_categorias(token)
    return templates.TemplateResponse(
        "categoria_form.html",
        {
            "request": request,
            "categorias": categorias,
            "categoria": None,
            **get_template_context(request)
        }
    )


@router.get("/json")
def listar_categorias_json(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    try:
        categorias = list_categorias(token)
        # Transformamos a dict simple
        data = [{"id": c.get("id"), "nombre": c.get("nombre")} for c in categorias]
        return JSONResponse(content=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": "No se pudieron cargar las categorías"}, status_code=500)

@router.get("/{categoria_id}", response_class=HTMLResponse)
def editar_form(request: Request, categoria_id: str):
    print("🚀📄📡 LLEGO A CATEGORIA:")
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    categoria_obj = get_categoria(token, categoria_id)
    categoria = SimpleNamespace(**categoria_obj) if categoria_obj else None
    categorias = list_categorias(token)
    return templates.TemplateResponse(
        "categoria_form.html",
        {
            "request": request,
            "categorias": categorias,
            "categoria": categoria,
            **get_template_context(request)  # 👈 para llenar el formulario
        }
    )

@router.post("", response_class=HTMLResponse)
def crear(
    request: Request,
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    posicion: int = Form(...),
    activa: Optional[bool] = Form(False),
    categoriaId: Optional[str] = Form(None)
):
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    # Decodificar token para obtener restaurante_id
    decoded = jwt.decode(token, options={"verify_signature": False})
    restaurante_id = decoded.get("restaurant_id")

    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "posicion": posicion,
        "activa": activa,
        "restaurante_id": restaurante_id  # 🔑 ahora sí se envía
    }
    

    if categoriaId:
        resultado = update_categoria(token, categoriaId, payload)
    else:
        resultado = create_categoria(token, payload)

    categorias = list_categorias(token)

    if "error" in resultado:
        return templates.TemplateResponse(
            "categoria_form.html",
            {
                "request": request, 
                "categorias": categorias, 
                "error": resultado["detalle"],
                **get_template_context(request)}
        )

    return templates.TemplateResponse(
        "categoria_form.html",
        {
            "request": request, 
            "categorias": categorias, 
            "success": "Operación realizada correctamente",
            **get_template_context(request)},
        
    )

@router.post("/editar/{categoria_id}", response_class=HTMLResponse)
def editar(
    request: Request,
    categoria_id: str,
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    posicion: int = Form(...),
    activa: Optional[bool] = Form(False),
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "posicion": posicion,
        "activa": activa
    }

    resultado = update_categoria(token, categoria_id, payload)
    categorias = list_categorias(token)

    if "error" in resultado:
        return templates.TemplateResponse(
            "categoria_form.html",
            {
                "request": request,
                "categorias": categorias,
                "error": resultado["detalle"],
                **get_template_context(request)
            }
        )

    return templates.TemplateResponse(
        "categoria_form.html",
        {
            "request": request,
            "categorias": categorias,
            "success": "Categoría actualizada correctamente",
            **get_template_context(request)
        }
    )


@router.post("/eliminar/{categoria_id}", response_class=HTMLResponse)
def eliminar(request: Request, categoria_id: str):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    resultado = delete_categoria(token, categoria_id)
    categorias = list_categorias(token)

    if "error" in resultado:
        return templates.TemplateResponse(
            "categoria_form.html",
            {
                "request": request,
                "categorias": categorias,
                "error": resultado["detalle"],
                **get_template_context(request)
            }
        )

    return templates.TemplateResponse(
        "categoria_form.html",
        {
            "request": request,
            "categorias": categorias,
            "success": "Categoría eliminada correctamente",
            **get_template_context(request)
        }
    )