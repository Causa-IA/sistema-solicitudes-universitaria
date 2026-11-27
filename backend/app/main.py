
from fastapi import FastAPI, HTTPException, Depends

from app.database.connection import verificar_conexion
from app.database.connection import Base, engine
from app import models
from app.routes.auth import router as auth_router
from app.core.dependencies import obtener_usuario_actual
from app.core.dependencies import permitir_roles
from app.routes.usuarios import router as usuarios_router
from app.routes.categorias import router as categorias_router
from app.routes.solicitudes import router as solicitudes_router
from app.routes.notificaciones import router as notificaciones_router
from app.routes.reportes import router as reportes_router



Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión de Solicitudes Universitarias",
    description="API para gestionar servicios y solicitudes universitarias",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(categorias_router)
app.include_router(solicitudes_router)
app.include_router(notificaciones_router)
app.include_router(reportes_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Sistema de solicitudes universitarias funcionando"
    }


@app.get("/health/database")
def estado_database():
    try:
        version = verificar_conexion()

        return {
            "estado": "Conectado",
            "database": "Neon PostgreSQL",
            "version": version
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible conectar con PostgreSQL"
        )
    

@app.get("/auth/me")
def obtener_perfil(usuario=Depends(obtener_usuario_actual)):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre
    }

@app.get("/prueba/admin")
def ruta_administrador(
    usuario=Depends(permitir_roles("Administrador"))
):
    return {
        "mensaje": "Acceso autorizado",
        "usuario": usuario.nombre,
        "rol": usuario.rol.nombre
    }

