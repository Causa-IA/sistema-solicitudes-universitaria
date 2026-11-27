
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Usuario, Rol
from app.schemas.usuario import UsuarioCrear, UsuarioActualizar, UsuarioRespuesta
from app.core.security import generar_password_hash
from app.core.dependencies import permitir_roles

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(permitir_roles("Administrador"))]
)


@router.post("/", response_model=UsuarioRespuesta)
def crear_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.correo == datos.correo).first():
        raise HTTPException(400, "El correo ya está registrado")

    rol = db.query(Rol).filter(Rol.id == datos.id_rol, Rol.activo == True).first()
    if not rol:
        raise HTTPException(404, "El rol no existe o está inactivo")

    usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        correo=datos.correo,
        password_hash=generar_password_hash(datos.password),
        id_rol=datos.id_rol
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=list[UsuarioRespuesta])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def consultar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if "correo" in cambios:
        existente = db.query(Usuario).filter(
            Usuario.correo == cambios["correo"],
            Usuario.id != usuario_id
        ).first()
        if existente:
            raise HTTPException(400, "El correo ya está registrado")

    if "id_rol" in cambios:
        rol = db.query(Rol).filter(
            Rol.id == cambios["id_rol"],
            Rol.activo == True
        ).first()
        if not rol:
            raise HTTPException(404, "El rol no existe o está inactivo")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario
