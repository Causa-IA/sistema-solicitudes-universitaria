
from getpass import getpass

from app.database.connection import SessionLocal
from app.models import Usuario, Rol
from app.core.security import generar_password_hash


def crear_usuario_prueba():
    db = SessionLocal()

    try:
        correo = input("Correo del estudiante: ").strip().lower()

        existente = db.query(Usuario).filter_by(
            correo=correo
        ).first()

        if existente:
            print("Ya existe un usuario con ese correo.")
            return

        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        password = getpass("Contraseña: ")

        rol = db.query(Rol).filter_by(
            nombre="Estudiante"
        ).first()

        if not rol:
            print("No existe el rol Estudiante.")
            return

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=generar_password_hash(password),
            id_rol=rol.id
        )

        db.add(usuario)
        db.commit()

        print("Usuario de prueba creado correctamente.")

    except Exception as error:
        db.rollback()
        print(f"Error: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    crear_usuario_prueba()
