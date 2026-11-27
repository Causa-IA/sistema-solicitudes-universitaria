
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class HistorialSolicitud(Base):
    __tablename__ = "historial_solicitudes"

    id = Column(Integer, primary_key=True, index=True)

    id_solicitud = Column(
        Integer,
        ForeignKey("solicitudes.id"),
        nullable=False
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    estado_anterior = Column(String(30), nullable=True)
    estado_nuevo = Column(String(30), nullable=False)
    observacion = Column(Text, nullable=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now())

    solicitud = relationship("Solicitud", backref="historial")
    usuario = relationship("Usuario", backref="acciones_historial")
