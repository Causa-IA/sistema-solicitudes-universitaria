
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    id_funcionario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    descripcion = Column(Text, nullable=False)
    prioridad = Column(String(20), nullable=False)
    estado = Column(String(30), default="REGISTRADA", nullable=False)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship(
        "Usuario",
        foreign_keys=[id_usuario],
        backref="solicitudes_creadas"
    )

    funcionario = relationship(
        "Usuario",
        foreign_keys=[id_funcionario],
        backref="solicitudes_asignadas"
    )

    categoria = relationship("Categoria", back_populates="solicitudes")
