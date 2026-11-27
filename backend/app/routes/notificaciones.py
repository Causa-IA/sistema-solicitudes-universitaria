from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Notificacion, Usuario
from app.schemas.notificacion import (
    NotificacionRespuesta,
    NotificacionActualizar
)
from app.core.dependencies import obtener_usuario_actual

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("/", response_model=list[NotificacionRespuesta])
def listar_notificaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    return db.query(Notificacion).filter(
        Notificacion.id_usuario == usuario.id
    ).order_by(Notificacion.fecha_creacion.desc()).all()


@router.put("/{notificacion_id}", response_model=NotificacionRespuesta)
def marcar_notificacion(
    notificacion_id: int,
    datos: NotificacionActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    notificacion = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.id_usuario == usuario.id
    ).first()

    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notificacion.leida = datos.leida
    db.commit()
    db.refresh(notificacion)

    return notificacion