"""Rutas para manejar las operaciones CRUD de PRODUCTOS."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import is_admin
from app.database import SessionLocal
from app.schemas import ProductCreate, ProductOut
from app.functions.crud_products import (
    list_products,
    get_prodct,
    create_product,
    get_product_by_name,
    update_product_by_id,
    delete_product,
)


router = APIRouter()


def get_db():
    """Genera una sesión de base de datos por solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ProductOut], tags=["Products"])
def read_all_products(db: Session = Depends(get_db)):
    """Listar todos los PRODUCTOS"""
    return list_products(db)


@router.get("/search", response_model=List[ProductOut], tags=["Products"])
def search_products(nombre: str, db: Session = Depends(get_db)):
    """Buscar producto por coincidencia parcial en el nombre."""
    return get_product_by_name(db, nombre)


@router.get("/{product_id}", response_model=ProductOut, tags=["Products"])
def read_product_detail(product_id: int, db: Session = Depends(get_db)):
    """Obtener los detalles de un producto específico."""
    return get_prodct(db, product_id)


@router.post("/", response_model=ProductOut, status_code=201, tags=["Products"])
def create_new_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(is_admin),
):
    """Crear un nuevo producto."""
    return create_product(db, product_in)


@router.put("/{product_id}", response_model=ProductOut, tags=["Products"])
def update_existing_product(
    product_id: int,
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(is_admin),
):
    """Actualizar un producto existente."""
    return update_product_by_id(db, product_id, product_in)


@router.delete("/{product_id}", status_code=204, tags=["Products"])
def delete_existing_product(
    product_id: int, db: Session = Depends(get_db), _: dict = Depends(is_admin)
):
    """Eliminar un producto."""
    delete_product(db, product_id)
