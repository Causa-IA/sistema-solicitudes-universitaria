
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class UsuarioLogin(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: EmailStr
    rol: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioLogin
