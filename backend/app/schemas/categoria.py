
from pydantic import BaseModel


class CategoriaCrear(BaseModel):
    nombre: str
    descripcion: str | None = None


class CategoriaActualizar(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    activo: bool | None = None


class CategoriaRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool

    class Config:
        from_attributes = True
