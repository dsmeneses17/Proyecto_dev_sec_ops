from pydantic import BaseModel, EmailStr

# Para registrar usuario
class UserCreate(BaseModel):
    usuario: str
    email: EmailStr
    password: str

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
        orm_mode = True