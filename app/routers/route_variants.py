"""Rutas para manejar las operaciones CRUD de variantes."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import is_admin
from app.database import SessionLocal

from app.schemas import VarianteCreate, VarianteOut
from app.functions.crud_variants import (
    list_variants,
    get_variant_by_id,
    create_variant,
    get_variant_by_sku,
    update_variant_by_id,
    delete_variant_by_id,
)

router = APIRouter()


def get_db():
    """Genera una sesión de base de datos por solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[VarianteOut], tags=["Variantes"])
def read_all_variants(db: Session = Depends(get_db)):
    """Listar todas las variantes."""
    return list_variants(db)


@router.get("/search", response_model=List[VarianteOut], tags=["Variantes"])
def read_variant_id_detail(variant_id: int, db: Session = Depends(get_db)):
    """Buscar variante por ID."""
    return get_variant_by_id(db, variant_id)


@router.get("/{variant_sku}", response_model=List[VarianteOut], tags=["Variantes"])
def read_variant_sku_detail(variant_sku: str, db: Session = Depends(get_db)):
    """Obtener detalles de una variante específica."""
    return get_variant_by_sku(db, variant_sku)


# @router.post("/", response_model=VarianteOut, status_code=201, tags=["Variantes"])
# def create_new_variant(
#     variant_in: VarianteCreate,
#     db: Session = Depends(get_db),
#     # _: dict = Depends(is_admin),
# ):
#     """Crear una nueva variante."""
#     return create_variant(db, variant_in)


@router.put("/{variant_id}", response_model=VarianteOut, tags=["Variantes"])
def update_existing_variant(
    variant_id: int,
    variant_in: VarianteCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(is_admin),
):
    """Actualizar una variante existente."""
    return update_variant_by_id(db, variant_id, variant_in)


@router.delete("/{variant_id}", status_code=204, tags=["Variantes"])
def delete_existing_variant(
    variant_id: int, db: Session = Depends(get_db), _: dict = Depends(is_admin)
):
    """Eliminar una variante."""
    delete_variant_by_id(db, variant_id)
