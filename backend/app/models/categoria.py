
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)

    solicitudes = relationship("Solicitud", back_populates="categoria")
