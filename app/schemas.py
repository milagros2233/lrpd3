"""Esquemas para el manejo de información para la base de datos"""

# pylint: disable=no-self-argument
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class CategoryCreate(BaseModel):
    """Esquema base para la categoria (Entrada)"""

    nombre_categoria: str
    logo_categoria: str

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


class CategoryOut(BaseModel):
    """Esquema para devolver los datos de una Categoria (salida)"""

    id: int
    nombre_categoria: str
    logo_categoria: str

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


class ProductCreate(BaseModel):
    """Esquema base para la categoria de un producto (Entrada)"""

    nombre_producto: str
    descripcion_producto: str
    precio_producto: float
    precio_oferta_producto: Optional[float] = None
    imagen_url_producto: str
    activo: bool = True
    categoria_id: int
    variantes: Optional[List["VarianteCreate"]] = None

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


class ProductOut(BaseModel):
    """Esquema base para la categoria de un producto (Salida)"""

    id: int
    nombre_producto: str
    descripcion_producto: str
    precio_producto: float
    precio_oferta_producto: Optional[float] = None
    imagen_url_producto: str
    activo: bool
    categoria: Optional["CategoryOut"]
    variantes: List["VarianteOut"]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


class VarianteCreate(BaseModel):
    """Esquema base para la variante de un producto (Entrada)"""

    color: str
    talla: str
    stock_variante_producto: int

    @field_validator("stock_variante_producto")
    def stock_mayor_cero(cls, v):
        """Valida que el stock sea 0 o mayor"""
        if v < 0:
            raise ValueError("El stock debe ser 0 o mayor")
        return v

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


class VarianteOut(BaseModel):
    """Esquema base para la variante de un producto (Salida)"""

    id: int
    color: str
    talla: str
    stock_variante_producto: int
    sku: Optional[str] = None
    producto_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Leer archivos ORM de SQLAlchemy, no solo dicts"""

        from_attributes = True


ProductOut.update_forward_refs()
