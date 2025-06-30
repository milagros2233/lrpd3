"""Rutas para manejar las operaciones CRUD de categorías."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import is_admin
from app.database import SessionLocal
from app.schemas import CategoryCreate, CategoryOut
from app.functions.crud_category import (
    list_categories,
    get_category_by_id,
    create_category,
    get_category_by_name,
    update_category_by_id,
    delete_category_by_id,
)


router = APIRouter()


def get_db():
    """Genera una sesión de base de datos por solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CategoryOut], tags=["Categories"])
def read_all_categories(db: Session = Depends(get_db)):
    """Listar todas las categorías."""
    return list_categories(db)


@router.get("/{category_id}", response_model=CategoryOut, tags=["Categories"])
def read_category_detail(category_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de una categoría específica."""
    return get_category_by_id(db, category_id)


@router.get("/search", response_model=List[CategoryOut], tags=["Categories"])
def search_categories(nombre: str, db: Session = Depends(get_db)):
    """Buscar categorías por coincidencia parcial en el nombre."""
    return get_category_by_name(db, nombre)


@router.post("/", response_model=CategoryOut, status_code=201, tags=["Categories"])
def create_new_category(
    cat_in: CategoryCreate, db: Session = Depends(get_db), _: dict = Depends(is_admin)
):
    """Crear una nueva categoría."""
    return create_category(db, cat_in)


@router.put("/{category_id}", response_model=CategoryOut, tags=["Categories"])
def update_existing_category(
    category_id: int,
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(is_admin),
):
    """Actualizar una categoría existente."""
    return update_category_by_id(db, category_id, cat_in)


@router.delete("/{category_id}", status_code=204, tags=["Categories"])
def delete_existing_category(
    category_id: int, db: Session = Depends(get_db), _: dict = Depends(is_admin)
):
    """Eliminar una categoría."""
    delete_category_by_id(db, category_id)
