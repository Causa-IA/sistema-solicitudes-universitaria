from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models import Solicitud, Categoria
from app.core.dependencies import permitir_roles

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/solicitudes")
def reporte_solicitudes(
    db: Session = Depends(get_db),
    usuario=Depends(permitir_roles("Administrador", "Supervisor"))
):
    total = db.query(func.count(Solicitud.id)).scalar()

    por_estado = db.query(
        Solicitud.estado,
        func.count(Solicitud.id)
    ).group_by(Solicitud.estado).all()

    por_prioridad = db.query(
        Solicitud.prioridad,
        func.count(Solicitud.id)
    ).group_by(Solicitud.prioridad).all()

    por_categoria = db.query(
        Categoria.nombre,
        func.count(Solicitud.id)
    ).join(
        Solicitud, Solicitud.id_categoria == Categoria.id
    ).group_by(Categoria.nombre).all()

    return {
        "total_solicitudes": total,
        "por_estado": [
            {"estado": estado, "cantidad": cantidad}
            for estado, cantidad in por_estado
        ],
        "por_prioridad": [
            {"prioridad": prioridad, "cantidad": cantidad}
            for prioridad, cantidad in por_prioridad
        ],
        "por_categoria": [
            {"categoria": categoria, "cantidad": cantidad}
            for categoria, cantidad in por_categoria
        ]
    }