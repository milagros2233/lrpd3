"""Archivo para centralizar la invalidación caché"""

import os
import json
from typing import Any, Optional
from app.cache.admin import redis_connection

DEFAULT_TTL = int(os.getenv("TTL_DETAIL", str(60 * 10)))

CATEGORIES = "categories"
CATEGORY = "category"

PRODUCTS = "products"
PRODUCT = "product"

VARIANTS = "variants"
VARIANT = "variant"

# -----------------------------
# GENERACIÓN DE CLAVES
# -----------------------------


def make_key(
    resource: str, resource_id: Optional[Any] = None, suffix: str = "all"
) -> str:
    """
    Construye una key de Redis estándar:
      - Para lista:   resource:all
      - Para detalle: resource:<id>
    """
    if resource_id is None:
        return f"{resource}:{suffix}"
    return f"{resource}:{resource_id}"


def make_search_key(resource: str, search_term: str) -> str:
    """Clave para búsquedas por nombre o término."""
    return f"{resource}:search:{search_term.lower()}"


# -----------------------------
# OPERACIONES GENÉRICAS DE CACHÉ
# -----------------------------


def get_cache(key: str) -> Optional[Any]:
    """Obtiene cualquier valor desde Redis usando la clave dada."""
    data = redis_connection.get(key)
    return json.loads(data) if data else None


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Guarda cualquier valor en Redis serializado como JSON."""
    redis_connection.set(key, json.dumps(value), ex=ttl)


# -----------------------------
# INVALIDACIÓN DE CACHÉ
# -----------------------------


def invalidate_cache(
    resource: str, resource_id: Optional[Any] = None, suffix: str = "all"
) -> None:
    """Elimina una clave específica del recurso."""
    key = make_key(resource, resource_id, suffix)
    redis_connection.delete(key)


def invalidate_pattern(resource: str, pattern_suffix: str = "*") -> None:
    """Elimina todas las claves que coincidan con el patrón (usa wildcard)."""
    pattern = f"{resource}:{pattern_suffix}"
    keys = redis_connection.keys(pattern)
    if keys:
        redis_connection.delete(*keys)
