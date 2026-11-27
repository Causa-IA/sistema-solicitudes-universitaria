
from pydantic import BaseModel, EmailStr


class UsuarioCrear(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    password: str
    id_rol: int


class UsuarioActualizar(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None
    id_rol: int | None = None
    activo: bool | None = None


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: EmailStr
    id_rol: int
    activo: bool

    class Config:
        from_attributes = True
