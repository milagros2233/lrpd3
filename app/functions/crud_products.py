"""CRUD para manejar las operaciones en la base de datos de productos"""

import logging
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.functions.crud_variants import generar_sku
from app.models import Producto, VarianteProducto
from app.schemas import ProductCreate, ProductOut

from app.cache.cache_for_products import (
    get_products_from_cache,
    set_products_cache,
    get_product_from_cache_by_id,
    set_product_cache_by_id,
    get_product_search_cache,
    set_product_search_cache,
)
from app.cache.cache_utils import (
    invalidate_cache,
    invalidate_pattern,
    DEFAULT_TTL,
    PRODUCT,
    PRODUCTS,
)

logger = logging.getLogger(__name__)


def list_products(db: Session) -> List[ProductOut]:
    """Devuelve todas los productos, intentando primero el cache."""
    cached = get_products_from_cache()
    if cached:
        logger.info("✅ Cache HIT: productos desde Redis")
        return cached

    logger.info("❌ Cache MISS: consultando base de datos")

    orm_list = db.query(Producto).all()
    out = [ProductOut.model_validate(p) for p in orm_list]
    set_products_cache(out, ttl=DEFAULT_TTL)
    return out


def get_prodct(db: Session, product_id: int) -> ProductOut:
    """Devuelve una producto por ID, con cache individual."""
    cached = get_product_from_cache_by_id(product_id)
    if cached:
        logger.info("✅ Cache HIT: producto %s desde Redis", product_id)
        return cached

    orm_product = db.query(Producto).filter(Producto.id == product_id).first()
    if not orm_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {product_id} no encontrada",
        )
    out = ProductOut.model_validate(orm_product)
    set_product_cache_by_id(out, ttl=DEFAULT_TTL)
    return out


def get_product_by_name(
    db: Session, search_term: str, limit: int = 20
) -> List[ProductOut]:
    """Busca productos que contengan el término en su nombre, ignorando mayúsculas y ordenando."""
    cached = get_product_search_cache(search_term)
    if cached:
        logger.info("✅ Cache HIT: búsqueda '%s' en Redis", search_term)
        return cached

    logger.info("❌ Cache MISS: búsqueda '%s' en base de datos", search_term)

    orm_list = (
        db.query(Producto)
        .filter(func.lower(Producto.nombre_producto).like(f"%{search_term.lower()}%"))
        .order_by(Producto.nombre_producto.asc())
        .limit(limit)
        .all()
    )

    if not orm_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron productos que coincidan con '{search_term}'",
        )

    out = [ProductOut.model_validate(p) for p in orm_list]
    set_product_search_cache(out, search_term)
    return out


def create_product(db: Session, product_in: ProductCreate) -> ProductOut:
    """Crea un nuevo producto e invalida la lista en caché."""
    existing_product = (
        db.query(Producto).filter_by(nombre_producto=product_in.nombre_producto).first()
    )
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un producto con el nombre '{product_in.nombre_producto}'",
        )

    new = Producto(**product_in.dict(exclude={"variantes"}))
    db.add(new)
    db.commit()
    db.refresh(new)

    if product_in.variantes:
        for variante_in in product_in.variantes:
            variante_data = variante_in.dict()
            variante_data["producto_id"] = new.id
            variante_data["sku"] = generar_sku(
                new.id, variante_data["color"], variante_data["talla"]
            )
            new_variante = VarianteProducto(**variante_data)
            db.add(new_variante)
        db.commit()

    invalidate_cache(resource=PRODUCTS)
    invalidate_pattern(resource=PRODUCTS, pattern_suffix="search:*")

    # Asegurarse de incluir las variantes si el modelo lo requiere
    new_out = ProductOut.model_validate(new)

    set_product_cache_by_id(new_out, ttl=DEFAULT_TTL)
    return new_out


def update_product_by_id(
    db: Session, product_id: int, product_in: ProductCreate
) -> ProductOut:
    """Actualiza un producto existente y limpia su caché."""

    orm_product = db.query(Producto).filter(Producto.id == product_id).first()
    if not orm_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {product_id} no encontrado",
        )

    for k, v in product_in.dict(exclude_unset=True, exclude={"variantes"}).items():
        setattr(orm_product, k, v)

    db.commit()
    db.refresh(orm_product)

    invalidate_cache(resource=PRODUCTS)
    invalidate_cache(resource=PRODUCT, resource_id=product_id)
    invalidate_pattern(resource=PRODUCTS, pattern_suffix="search:*")

    out = ProductOut.model_validate(orm_product)
    set_product_cache_by_id(out, ttl=DEFAULT_TTL)
    return out


def delete_product(db: Session, product_id: int) -> None:
    """Elimina un producto existente y limpia si cache"""
    orm_product = db.query(Producto).get(product_id)
    if not orm_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(orm_product)
    db.commit()
    invalidate_cache(PRODUCTS)
    invalidate_cache(PRODUCT, product_id)
    invalidate_pattern(PRODUCTS, "search:*")
