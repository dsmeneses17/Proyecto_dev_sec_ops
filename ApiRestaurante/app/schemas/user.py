from pydantic import BaseModel, EmailStr, field_validator
import re

# Para registrar usuario
class UserCreate(BaseModel):
    nombre_completo: str
    usuario: str
    email: EmailStr
    password: str
    rol: str = "cliente"

    @field_validator("nombre_completo")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre completo es obligatorio")
        return v.strip()

    @field_validator("usuario")
    @classmethod
    def usuario_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError("El usuario solo puede contener letras, números, puntos, guiones y guiones bajos")
        return v

    @field_validator("password")
    @classmethod
    def password_seguro(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

# Para login
class UserLogin(BaseModel):
    usuario: str
    password: str

# Para devolver token
class Token(BaseModel):
    access_token: str
    token_type: str

# Opcional: para devolver datos del usuario
class UserOut(BaseModel):
    id: int
    usuario: str
    email: EmailStr
    role: str | None = None

    class Config:
        from_attributes = True