from datetime import datetime
from pydantic import BaseModel

class NotificacionRespuesta(BaseModel):
    id: int
    id_usuario: int
    id_solicitud: int | None
    mensaje: str
    leida: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class NotificacionActualizar(BaseModel):
    leida: bool