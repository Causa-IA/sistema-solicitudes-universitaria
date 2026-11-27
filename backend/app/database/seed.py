
from app.database.connection import SessionLocal
from app.models import Rol, Categoria


def cargar_datos():
    db = SessionLocal()

    try:
        # Roles iniciales
        roles = [
            ("Administrador", "Gestiona y administra el sistema"),
            ("Estudiante", "Registra y consulta sus solicitudes"),
            ("Funcionario", "Atiende las solicitudes asignadas"),
            ("Supervisor", "Supervisa la gestión de solicitudes")
        ]

        for nombre, descripcion in roles:
            existe = db.query(Rol).filter_by(nombre=nombre).first()

            if not existe:
                db.add(Rol(nombre=nombre, descripcion=descripcion))

        # Categorías iniciales
        categorias = [
            ("Académica", "Solicitudes relacionadas con asuntos académicos"),
            ("Financiera", "Solicitudes relacionadas con pagos y finanzas"),
            ("Tecnológica", "Solicitudes de soporte tecnológico"),
            ("Administrativa", "Solicitudes de trámites administrativos"),
            ("Bienestar universitario", "Solicitudes relacionadas con bienestar")
        ]

        for nombre, descripcion in categorias:
            existe = db.query(Categoria).filter_by(nombre=nombre).first()

            if not existe:
                db.add(Categoria(nombre=nombre, descripcion=descripcion))

        db.commit()
        print("Datos iniciales cargados correctamente")

    except Exception as error:
        db.rollback()
        print(f"Error al cargar los datos: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    cargar_datos()
