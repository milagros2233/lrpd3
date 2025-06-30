"""Modelo del servicio de productos para la base de datos"""

# pylint: disable=not-callable

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Float,
    ForeignKey,
    Boolean,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Categoria(Base):
    """Representa la entidad categoria"""

    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre_categoria = Column(String(255), nullable=False, unique=True, index=True)
    logo_categoria = Column(String(255), nullable=False)

    productos = relationship(
        "Producto", back_populates="categoria", cascade="all, delete"
    )


class Producto(Base):
    """Representa un producto con sus atributos generales"""

    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_producto = Column(String(100), nullable=False, unique=True, index=True)
    descripcion_producto = Column(String(255), nullable=False)
    precio_producto = Column(Float, nullable=False)
    precio_oferta_producto = Column(Float, nullable=True)
    imagen_url_producto = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    categoria = relationship("Categoria", back_populates="productos")
    variantes = relationship(
        "VarianteProducto", back_populates="producto", cascade="all, delete-orphan"
    )


class VarianteProducto(Base):
    """Representa una variante de un producto (color + talla + stock)"""

    __tablename__ = "variantes_producto"

    id = Column(Integer, primary_key=True, index=True)
    talla = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    stock_variante_producto = Column(Integer, nullable=False)
    sku = Column(String(30), unique=True, nullable=False, index=True)

    producto_id = Column(
        Integer, ForeignKey("productos.id", ondelete="CASCADE"), index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    producto = relationship("Producto", back_populates="variantes")

    __table_args__ = (
        UniqueConstraint("producto_id", "color", "talla", name="uq_variante_producto"),
    )
