
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    id_solicitud = Column(
        Integer,
        ForeignKey("solicitudes.id"),
        nullable=True
    )

    mensaje = Column(String(255), nullable=False)
    leida = Column(Boolean, default=False)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", backref="notificaciones")
    solicitud = relationship("Solicitud", backref="notificaciones")
