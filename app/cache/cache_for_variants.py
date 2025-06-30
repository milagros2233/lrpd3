"""Cache for Variants"""

from typing import List, Optional
from app.schemas import VarianteOut
from app.cache.cache_utils import (
    make_key,
    make_search_key,
    get_cache,
    set_cache,
    DEFAULT_TTL,
    VARIANT,
    VARIANTS,
)

# -----------------------------
# VARIANTE COMPLETAS
# -----------------------------


def get_variants_from_cache() -> Optional[List[VarianteOut]]:
    """
    Intenta obtener la lista completa de variantes desde Redis.
    Devuelve None si no existe en caché.
    """
    key = make_key(VARIANTS)
    data = get_cache(key)
    if not data:
        return None
    return [VarianteOut.model_validate(item) for item in data]


def set_variants_cache(variants: List[VarianteOut], ttl: int = DEFAULT_TTL) -> None:
    """
    Serializa y guarda la lista de variantes en Redis con un TTL.
    """
    key = make_key(VARIANTS)
    value = [variant.model_dump(mode="json") for variant in variants]
    set_cache(key, value, ttl)


# -----------------------------
# VARIANTE POR ID
# -----------------------------


def get_variant_from_cache_by_id(variant_id: int) -> Optional[VarianteOut]:
    """
    Intenta obtener una variante individual desde Redis.
    """
    key = make_key(VARIANT, variant_id)
    data = get_cache(key)
    return VarianteOut.model_validate(data) if data else None


def set_variant_cache_by_id(variant: VarianteOut, ttl: int = DEFAULT_TTL) -> None:
    """
    Guarda una variante individual en Redis.
    """
    key = make_key(VARIANT, variant.id)
    set_cache(key, variant.model_dump(mode="json"), ttl)


# -----------------------------
# BÚSQUEDAS POR SKU
# -----------------------------


def get_variant_search_cache(search_term: str) -> Optional[List[VarianteOut]]:
    """Obtiene una variante por termino buscado"""
    key = make_search_key(VARIANTS, search_term)
    data = get_cache(key)
    if not data:
        return None
    return [VarianteOut.model_validate(item) for item in data]


def set_variant_search_cache(
    variants: List[VarianteOut], search_term: str, ttl: int = DEFAULT_TTL
) -> None:
    """Envia dato de busqueda de cache"""
    key = make_search_key(VARIANTS, search_term)
    value = [variant.model_dump(mode="json") for variant in variants]
    set_cache(key, value, ttl)
