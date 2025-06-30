"""Cache for products"""

from typing import List, Optional
from app.schemas import ProductOut
from app.cache.cache_utils import (
    make_key,
    make_search_key,
    get_cache,
    set_cache,
    DEFAULT_TTL,
    PRODUCTS,
    PRODUCT,
)

# -----------------------------
# PRODUCTOS COMPLETAS
# -----------------------------


def get_products_from_cache() -> Optional[List[ProductOut]]:
    """
    Intenta obtener la lista completa de categorías desde Redis.
    Devuelve None si no existe en caché.
    """
    key = make_key(PRODUCTS)
    data = get_cache(key)
    if not data:
        return None
    return [ProductOut.model_validate(item) for item in data]


def set_products_cache(products: List[ProductOut], ttl: int = DEFAULT_TTL) -> None:
    """Serializa y guarda la lista de PRODUCTOS en Redis con un TTL."""
    key = make_key(PRODUCTS)
    value = [cat.model_dump(mode="json") for cat in products]
    set_cache(key, value, ttl)


# -----------------------------
# PRODUCTO POR ID
# -----------------------------


def get_product_from_cache_by_id(product_id: int) -> Optional[ProductOut]:
    """Intenta obtener un PRODUCTO individual desde Redis."""
    key = make_key(PRODUCT, product_id)
    data = get_cache(key)
    return ProductOut.model_validate(data) if data else None


def set_product_cache_by_id(product: ProductOut, ttl: int = DEFAULT_TTL) -> None:
    """Guarda un PRODUCTO individual en Redis."""
    key = make_key(PRODUCT, product.id)
    set_cache(key, product.model_dump(mode="json"), ttl)


# -----------------------------
# BÚSQUEDAS POR NOMBRE
# -----------------------------


def get_product_search_cache(search_term: str) -> Optional[List[ProductOut]]:
    """Obtiene una categoria por termino buscado"""
    key = make_search_key(PRODUCTS, search_term)
    data = get_cache(key)
    if not data:
        return None
    return [ProductOut.model_validate(item) for item in data]


def set_product_search_cache(
    categories: List[ProductOut], search_term: str, ttl: int = DEFAULT_TTL
) -> None:
    """Envia dato de busqueda de cache"""
    key = make_search_key(PRODUCTS, search_term)
    value = [cat.model_dump(mode="json") for cat in categories]

    if value:
        set_cache(key, value, ttl)
