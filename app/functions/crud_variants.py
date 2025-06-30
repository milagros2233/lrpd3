"""CRUD para manejar las operaciones en la base de datos de variantes"""

import logging
import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import VarianteProducto
from app.schemas import VarianteCreate, VarianteOut
from app.cache.cache_for_variants import (
    get_variants_from_cache,
    set_variants_cache,
    get_variant_from_cache_by_id,
    set_variant_cache_by_id,
    get_variant_search_cache,
    set_variant_search_cache,
)
from app.cache.cache_utils import (
    invalidate_cache,
    invalidate_pattern,
    DEFAULT_TTL,
    VARIANT,
    VARIANTS,
)

logger = logging.getLogger(__name__)


def list_variants(db: Session) -> List[VarianteOut]:
    """Devuelve todas las variantes, intentando primero el cache."""
    variants = get_variants_from_cache()
    if variants is not None:
        logger.info("✅ Cache HIT: variantes desde Redis")
        return variants

    logger.info("❌ Cache MISS: consultando base de datos")

    orm_list = db.query(VarianteProducto).all()
    out_list = [VarianteOut.model_validate(c) for c in orm_list]
    set_variants_cache(out_list, ttl=DEFAULT_TTL)
    return out_list


def get_variant_by_id(db: Session, variant_id: int) -> VarianteOut:
    """Devuelve una variante por ID, con cache individual."""
    variante = get_variant_from_cache_by_id(variant_id)
    if variante:
        logger.info("✅ Cache HIT: VARIANTE %s desde Redis", variant_id)
        return variante

    orm_variant = (
        db.query(VarianteProducto).filter(VarianteProducto.id == variant_id).first()
    )
    if not orm_variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variante Producto {variant_id} no encontrada",
        )
    out = VarianteOut.model_validate(orm_variant)
    set_variant_cache_by_id(out, ttl=DEFAULT_TTL)
    return out


def get_variant_by_sku(
    db: Session, search_sku: str, limit: int = 20
) -> List[VarianteOut]:
    """Busca variantes que contengan el SKU, ignorando mayúsculas y ordenando."""
    cached = get_variant_search_cache(search_sku)

    if cached:
        logger.info("✅ Cache HIT: búsqueda '%s' en Redis", search_sku)
        return cached

    logger.info("❌ Cache MISS: búsqueda '%s' en base de datos", search_sku)

    orm_list = (
        db.query(VarianteProducto)
        .filter(func.lower(VarianteProducto.sku).like(f"%{search_sku.lower()}%"))
        .order_by(VarianteProducto.sku.asc())
        .limit(limit)
        .all()
    )

    if not orm_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron categorías que coincidan con '{search_sku}'",
        )

    out = [VarianteOut.model_validate(variant) for variant in orm_list]
    set_variant_search_cache(out, search_sku)
    return out


def generar_sku(producto_id: int, color: str, talla: str) -> str:
    """Genera un SKU único basado en el producto, color y talla"""
    return f"P{producto_id}-{color[:3].upper()}-{talla[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"


def create_variant(db: Session, variant: VarianteCreate) -> VarianteOut:
    """Crear una variante, verificando que no exista duplicado y generando SKU automáticamente."""

    exists = (
        db.query(VarianteProducto)
        .filter_by(
            producto_id=variant.producto_id, color=variant.color, talla=variant.talla
        )
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una variante con ese color y talla para el producto.",
        )

    sku = generar_sku(
        producto_id=variant.producto_id, color=variant.color, talla=variant.talla
    )

    new = VarianteProducto(
        color=variant.color,
        talla=variant.talla,
        stock_variante_producto=variant.stock_variante_producto,
        producto_id=variant.producto_id,
        sku=sku,
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    invalidate_cache(resource=VARIANTS)
    new_out = VarianteOut.model_validate(new)
    set_variant_cache_by_id(new_out, ttl=DEFAULT_TTL)
    invalidate_pattern(resource=VARIANTS, pattern_suffix="search:*")
    return new_out


def update_variant_by_id(
    db: Session, variant_id: int, variant: VarianteCreate
) -> VarianteOut:
    """Actualiza una variante existente, validando unicidad y regenerando SKU si es necesario."""
    orm_variant = db.query(VarianteProducto).filter_by(id=variant_id).first()

    producto_id = orm_variant.producto_id

    if not orm_variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variante con ID {variant_id} no encontrada.",
        )

    duplicate = (
        db.query(VarianteProducto)
        .filter(
            VarianteProducto.producto_id == producto_id,
            VarianteProducto.color == variant.color,
            VarianteProducto.talla == variant.talla,
            VarianteProducto.id != variant_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otra variante con ese color y talla para el producto.",
        )

    orm_variant.color = variant.color
    orm_variant.talla = variant.talla
    orm_variant.stock_variante_producto = variant.stock_variante_producto
    orm_variant.sku = generar_sku(
        producto_id=producto_id, color=variant.color, talla=variant.talla
    )

    db.commit()
    db.refresh(orm_variant)

    invalidate_cache(resource=VARIANTS)
    invalidate_cache(resource=VARIANT, resource_id=variant_id)
    updated = VarianteOut.model_validate(orm_variant)
    set_variant_cache_by_id(updated, ttl=DEFAULT_TTL)
    invalidate_pattern(resource=VARIANTS, pattern_suffix="search:*")
    return updated


def delete_variant_by_id(db: Session, variant_id: int) -> None:
    """Elimina una variante y purga su cache."""
    orm_variant = (
        db.query(VarianteProducto).filter(VarianteProducto.id == variant_id).first()
    )
    if not orm_variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VARIANTE {variant_id} no encontrada",
        )
    db.delete(orm_variant)
    db.commit()

    invalidate_cache(resource=VARIANTS)
    invalidate_cache(resource=VARIANT, resource_id=variant_id)
    invalidate_pattern(resource=VARIANTS, pattern_suffix="search:*")
