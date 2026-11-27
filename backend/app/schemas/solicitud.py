
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class SolicitudCrear(BaseModel):
    id_categoria: int
    descripcion: str
    prioridad: Literal["BAJA", "MEDIA", "ALTA"]


class SolicitudActualizar(BaseModel):
    id_categoria: int | None = None
    descripcion: str | None = None
    prioridad: Literal["BAJA", "MEDIA", "ALTA"] | None = None


class SolicitudRespuesta(BaseModel):
    id: int
    codigo: str
    id_usuario: int
    id_categoria: int
    id_funcionario: int | None
    descripcion: str
    prioridad: str
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class SolicitudAsignar(BaseModel):
    id_funcionario: int


class SolicitudCambiarEstado(BaseModel):
    estado: str
    observacion: str | None = None

class HistorialRespuesta(BaseModel):
    id: int
    id_solicitud: int
    id_usuario: int
    nombre_usuario: str
    estado_anterior: str | None
    estado_nuevo: str
    observacion: str | None
    fecha: datetime