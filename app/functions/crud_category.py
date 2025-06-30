"""CRUD para manejar las operaciones en la base de datos de categorias"""

import logging
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Categoria
from app.schemas import CategoryCreate, CategoryOut
from app.cache.cache_for_category import (
    get_categories_from_cache,
    set_categories_cache,
    get_category_from_cache_by_id,
    set_category_cache_by_id,
    get_category_search_cache,
    set_category_search_cache,
)
from app.cache.cache_utils import (
    invalidate_cache,
    invalidate_pattern,
    DEFAULT_TTL,
    CATEGORY,
    CATEGORIES,
)

logger = logging.getLogger(__name__)


def list_categories(db: Session) -> List[CategoryOut]:
    """Devuelve todas las categorías, intentando primero el cache."""
    cats = get_categories_from_cache()
    if cats is not None:
        logger.info("✅ Cache HIT: categorías desde Redis")
        return cats

    logger.info("❌ Cache MISS: consultando base de datos")

    orm_list = db.query(Categoria).all()
    out_list = [CategoryOut.model_validate(c) for c in orm_list]
    set_categories_cache(out_list, ttl=DEFAULT_TTL)
    return out_list


def get_category_by_id(db: Session, category_id: int) -> CategoryOut:
    """Devuelve una categoría por ID, con cache individual."""
    cat = get_category_from_cache_by_id(category_id)
    if cat:
        logger.info("✅ Cache HIT: categoría %s desde Redis", category_id)
        return cat

    orm_cat = db.query(Categoria).filter(Categoria.id == category_id).first()
    if not orm_cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría {category_id} no encontrada",
        )
    out = CategoryOut.model_validate(orm_cat)
    set_category_cache_by_id(out, ttl=DEFAULT_TTL)
    return out


def get_category_by_name(
    db: Session, search_term: str, limit: int = 20
) -> List[CategoryOut]:
    """Busca categorías que contengan el término en su nombre, ignorando mayúsculas y ordenando."""
    cached = get_category_search_cache(search_term)

    if cached:
        logger.info("✅ Cache HIT: búsqueda '%s' en Redis", search_term)
        return cached

    logger.info("❌ Cache MISS: búsqueda '%s' en base de datos", search_term)

    orm_list = (
        db.query(Categoria)
        .filter(func.lower(Categoria.nombre_categoria).like(f"%{search_term.lower()}%"))
        .order_by(Categoria.nombre_categoria.asc())
        .limit(limit)
        .all()
    )

    if not orm_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron categorías que coincidan con '{search_term}'",
        )

    out = [CategoryOut.model_validate(categoria) for categoria in orm_list]
    set_category_search_cache(out, search_term)
    return out


def create_category(db: Session, cat_in: CategoryCreate) -> CategoryOut:
    """Crea una nueva categoría, e invalida la lista en cache."""
    new = Categoria(
        nombre_categoria=cat_in.nombre_categoria, logo_categoria=cat_in.logo_categoria
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    invalidate_cache(resource=CATEGORIES)
    new_out = CategoryOut.model_validate(new)
    set_category_cache_by_id(new_out, ttl=DEFAULT_TTL)
    invalidate_pattern(resource=CATEGORIES, pattern_suffix="search:*")
    return new_out


def update_category_by_id(
    db: Session, category_id: int, cat_in: CategoryCreate
) -> CategoryOut:
    """Actualiza una categoría existente y limpia su cache y la lista."""

    orm_cat = db.query(Categoria).filter(Categoria.id == category_id).first()
    if not orm_cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría {category_id} no encontrada",
        )
    orm_cat.nombre_categoria = cat_in.nombre_categoria
    orm_cat.logo_categoria = cat_in.logo_categoria
    db.commit()
    db.refresh(orm_cat)

    invalidate_cache(resource=CATEGORIES)
    invalidate_cache(resource=CATEGORY, resource_id=category_id)

    updated = CategoryOut.model_validate(orm_cat)
    set_category_cache_by_id(updated, ttl=DEFAULT_TTL)
    invalidate_pattern(resource=CATEGORIES, pattern_suffix="search:*")
    return updated


def delete_category_by_id(db: Session, category_id: int) -> None:
    """Elimina una categoría y purga su cache."""

    orm_cat = db.query(Categoria).filter(Categoria.id == category_id).first()
    if not orm_cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría {category_id} no encontrada",
        )
    db.delete(orm_cat)
    db.commit()

    invalidate_cache(resource=CATEGORIES)
    invalidate_cache(resource=CATEGORY, resource_id=category_id)
    invalidate_pattern(resource=CATEGORIES, pattern_suffix="search:*")
