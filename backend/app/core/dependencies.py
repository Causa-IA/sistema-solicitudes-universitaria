
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Usuario
from app.core.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise error_credenciales

    except JWTError:
        raise error_credenciales

    usuario = db.query(Usuario).filter(
        Usuario.id == int(usuario_id)
    ).first()

    if not usuario or not usuario.activo:
        raise error_credenciales

    return usuario


def permitir_roles(*roles_permitidos):
    def verificar_rol(
        usuario: Usuario = Depends(obtener_usuario_actual)
    ):
        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario

    return verificar_rol
