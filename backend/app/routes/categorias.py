
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Categoria
from app.schemas.categoria import (
    CategoriaCrear,
    CategoriaActualizar,
    CategoriaRespuesta
)
from app.core.dependencies import permitir_roles

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
    dependencies=[Depends(permitir_roles("Administrador"))]
)


@router.post("/", response_model=CategoriaRespuesta)
def crear_categoria(datos: CategoriaCrear, db: Session = Depends(get_db)):
    existente = db.query(Categoria).filter(
        Categoria.nombre == datos.nombre
    ).first()

    if existente:
        raise HTTPException(400, "La categoría ya existe")

    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("/", response_model=list[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()


@router.get("/{categoria_id}", response_model=CategoriaRespuesta)
def consultar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    return categoria


@router.put("/{categoria_id}", response_model=CategoriaRespuesta)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaActualizar,
    db: Session = Depends(get_db)
):
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if "nombre" in cambios:
        existente = db.query(Categoria).filter(
            Categoria.nombre == cambios["nombre"],
            Categoria.id != categoria_id
        ).first()

        if existente:
            raise HTTPException(400, "El nombre ya está registrado")

    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)
    return categoria
