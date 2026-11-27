
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database.connection import get_db
from app.models import Solicitud, Categoria, HistorialSolicitud, Usuario, Notificacion
from app.schemas.solicitud import (
    SolicitudCrear,
    SolicitudActualizar,
    SolicitudRespuesta,
    SolicitudAsignar,
    SolicitudCambiarEstado

)

from app.core.dependencies import obtener_usuario_actual, permitir_roles

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post("/", response_model=SolicitudRespuesta)
def crear_solicitud(
    datos: SolicitudCrear,
    db: Session = Depends(get_db),
    usuario=Depends(permitir_roles("Estudiante"))
):
    categoria = db.query(Categoria).filter(
        Categoria.id == datos.id_categoria,
        Categoria.activo == True
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    solicitud = Solicitud(
        codigo=f"SOL-{uuid.uuid4().hex[:10].upper()}",
        id_usuario=usuario.id,
        id_categoria=datos.id_categoria,
        descripcion=datos.descripcion,
        prioridad=datos.prioridad,
        estado="REGISTRADA"
    )

    db.add(solicitud)
    db.flush()

    historial = HistorialSolicitud(
        id_solicitud=solicitud.id,
        id_usuario=usuario.id,
        estado_anterior=None,
        estado_nuevo="REGISTRADA",
        observacion="Solicitud creada"
    )

    db.add(historial)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get("/", response_model=list[SolicitudRespuesta])
def listar_solicitudes(
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual)
):
    consulta = db.query(Solicitud)

    if usuario.rol.nombre == "Estudiante":
        consulta = consulta.filter(Solicitud.id_usuario == usuario.id)

    elif usuario.rol.nombre == "Funcionario":
        consulta = consulta.filter(Solicitud.id_funcionario == usuario.id)

    return consulta.all()


@router.get("/{solicitud_id}", response_model=SolicitudRespuesta)
def consultar_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual)
):
    solicitud = db.query(Solicitud).filter(
        Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(404, "Solicitud no encontrada")

    if usuario.rol.nombre == "Estudiante" and solicitud.id_usuario != usuario.id:
        raise HTTPException(403, "No tienes permiso para consultar esta solicitud")

    if usuario.rol.nombre == "Funcionario" and solicitud.id_funcionario != usuario.id:
        raise HTTPException(403, "Esta solicitud no está asignada a ti")

    return solicitud


@router.put("/{solicitud_id}", response_model=SolicitudRespuesta)
def actualizar_solicitud(
    solicitud_id: int,
    datos: SolicitudActualizar,
    db: Session = Depends(get_db),
    usuario=Depends(permitir_roles("Administrador"))
):
    solicitud = db.query(Solicitud).filter(
        Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(404, "Solicitud no encontrada")

    if solicitud.estado != "REGISTRADA":
        raise HTTPException(400, "Solo se pueden modificar solicitudes registradas")

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if "id_categoria" in cambios:
        categoria = db.query(Categoria).filter(
            Categoria.id == cambios["id_categoria"],
            Categoria.activo == True
        ).first()

        if not categoria:
            raise HTTPException(404, "Categoría no encontrada")

    for campo, valor in cambios.items():
        setattr(solicitud, campo, valor)

    db.commit()
    db.refresh(solicitud)
    return solicitud

@router.put("/{solicitud_id}/asignar", response_model=SolicitudRespuesta)
def asignar_solicitud(
    solicitud_id: int,
    datos: SolicitudAsignar,
    db: Session = Depends(get_db),
    usuario=Depends(permitir_roles("Administrador", "Supervisor"))
):
    solicitud = db.query(Solicitud).filter(
        Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(404, "Solicitud no encontrada")

    if solicitud.estado not in ["REGISTRADA", "ASIGNADA"]:
        raise HTTPException(400, "Solo se pueden asignar o reasignar solicitudes registradas o asignadas")

    funcionario = db.query(Usuario).filter(
        Usuario.id == datos.id_funcionario,
        Usuario.activo == True
    ).first()

    if not funcionario or funcionario.rol.nombre != "Funcionario":
        raise HTTPException(400, "El usuario no es un funcionario activo")

    estado_anterior = solicitud.estado
    solicitud.id_funcionario = funcionario.id

    if solicitud.estado == "REGISTRADA":
        solicitud.estado = "ASIGNADA"

    db.add(HistorialSolicitud(
        id_solicitud=solicitud.id,
        id_usuario=usuario.id,
        estado_anterior=estado_anterior,
        estado_nuevo=solicitud.estado,
        observacion=f"Solicitud asignada al funcionario {funcionario.nombre}"
    ))

    db.add(Notificacion(
        id_usuario=solicitud.id_usuario,
        id_solicitud=solicitud.id,
        mensaje=f"Tu solicitud {solicitud.codigo} ha sido asignada al funcionario {funcionario.nombre}."
    ))

    db.commit()
    db.refresh(solicitud)

    return solicitud


@router.put("/{solicitud_id}/estado", response_model=SolicitudRespuesta)
def cambiar_estado(
    solicitud_id: int,
    datos: SolicitudCambiarEstado,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual)
):
    transiciones = {
        "REGISTRADA": [],
        "ASIGNADA": ["EN PROCESO"],
        "EN PROCESO": ["RESUELTA"],
        "RESUELTA": ["CERRADA"],
        "CERRADA": ["REABIERTA"],
        "REABIERTA": ["EN PROCESO"]
    }

    solicitud = db.query(Solicitud).filter(
        Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(404, "Solicitud no encontrada")

    if usuario.rol.nombre not in ["Administrador", "Supervisor", "Funcionario"]:
        raise HTTPException(403, "No tienes permiso para cambiar estados")

    if datos.estado == "REABIERTA" and not datos.observacion:
        raise HTTPException(400, "Debes indicar el motivo de la reapertura")

    if datos.estado == "REABIERTA" and usuario.rol.nombre not in ["Administrador", "Supervisor"]:
        raise HTTPException(403, "Solo Administradores y Supervisores pueden reabrir solicitudes")

    if usuario.rol.nombre == "Funcionario" and solicitud.id_funcionario != usuario.id:
        raise HTTPException(403, "Esta solicitud no está asignada a ti")

    if datos.estado not in transiciones.get(solicitud.estado, []):
        raise HTTPException(400, "Transición de estado no permitida")

    if datos.estado == "RESUELTA" and not datos.observacion:
        raise HTTPException(400, "Debes registrar la solución realizada")

    estado_anterior = solicitud.estado
    solicitud.estado = datos.estado

    db.add(HistorialSolicitud(
        id_solicitud=solicitud.id,
        id_usuario=usuario.id,
        estado_anterior=estado_anterior,
        estado_nuevo=datos.estado,
        observacion=datos.observacion
    ))

    db.add(Notificacion(
    id_usuario=solicitud.id_usuario,
    id_solicitud=solicitud.id,
    mensaje=f"Tu solicitud {solicitud.codigo} cambió de estado a {datos.estado}."
    ))

    db.commit()
    db.refresh(solicitud)

    return solicitud

@router.get("/{solicitud_id}/historial")
def consultar_historial(
    solicitud_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    solicitud = db.query(Solicitud).filter(
        Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if usuario.rol.nombre == "Estudiante" and solicitud.id_usuario != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para consultar este historial")

    if usuario.rol.nombre == "Funcionario" and solicitud.id_funcionario != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para consultar este historial")

    historial = db.query(HistorialSolicitud).filter(
        HistorialSolicitud.id_solicitud == solicitud_id
    ).order_by(HistorialSolicitud.fecha.asc()).all()

    return [
        {
            "id": registro.id,
            "id_solicitud": registro.id_solicitud,
            "id_usuario": registro.id_usuario,
            "nombre_usuario": registro.usuario.nombre,
            "estado_anterior": registro.estado_anterior,
            "estado_nuevo": registro.estado_nuevo,
            "observacion": registro.observacion,
            "fecha": registro.fecha
        }
        for registro in historial
    ]


