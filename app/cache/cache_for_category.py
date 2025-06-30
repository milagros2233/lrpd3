"""Cache for categories"""

from typing import List, Optional
from app.schemas import CategoryOut
from app.cache.cache_utils import (
    make_key,
    make_search_key,
    get_cache,
    set_cache,
    DEFAULT_TTL,
    CATEGORIES,
    CATEGORY,
)

# -----------------------------
# CATEGORÍAS COMPLETAS
# -----------------------------


def get_categories_from_cache() -> Optional[List[CategoryOut]]:
    """
    Intenta obtener la lista completa de categorías desde Redis.
    Devuelve None si no existe en caché.
    """
    key = make_key(CATEGORIES)
    data = get_cache(key)
    if not data:
        return None
    return [CategoryOut.model_validate(item) for item in data]


def set_categories_cache(categories: List[CategoryOut], ttl: int = DEFAULT_TTL) -> None:
    """
    Serializa y guarda la lista de categorías en Redis con un TTL.
    """
    key = make_key(CATEGORIES)
    value = [cat.model_dump(mode="json") for cat in categories]
    set_cache(key, value, ttl)


# -----------------------------
# CATEGORÍA POR ID
# -----------------------------


def get_category_from_cache_by_id(category_id: int) -> Optional[CategoryOut]:
    """
    Intenta obtener una categoría individual desde Redis.
    """
    key = make_key(CATEGORY, category_id)
    data = get_cache(key)
    return CategoryOut.model_validate(data) if data else None


def set_category_cache_by_id(category: CategoryOut, ttl: int = DEFAULT_TTL) -> None:
    """
    Guarda una categoría individual en Redis.
    """
    key = make_key(CATEGORY, category.id)
    set_cache(key, category.model_dump(mode="json"), ttl)


# -----------------------------
# BÚSQUEDAS POR NOMBRE
# -----------------------------


def get_category_search_cache(search_term: str) -> Optional[List[CategoryOut]]:
    """Obtiene una categoria por termino buscado"""
    key = make_search_key(CATEGORIES, search_term)
    data = get_cache(key)
    if not data:
        return None
    return [CategoryOut.model_validate(item) for item in data]


def set_category_search_cache(
    categories: List[CategoryOut], search_term: str, ttl: int = DEFAULT_TTL
) -> None:
    """Envia dato de busqueda de cache"""
    key = make_search_key(CATEGORIES, search_term)
    value = [cat.model_dump(mode="json") for cat in categories]
    set_cache(key, value, ttl)
