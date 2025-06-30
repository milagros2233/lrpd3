"""Archivo inicial, Sercvicio de la API RESTful para el manejo de la base de datos"""

import logging
from sqlalchemy import inspect
from fastapi import FastAPI
from app.database import engine
from app.routers import route_category, route_products, route_variants
from app.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s › %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


inspector = inspect(engine)
tables = set(inspector.get_table_names())

for name, table in Base.metadata.tables.items():
    if name in tables:
        logger.info("Ya existe... se Omite : %s", name)
    else:
        logger.info("Creando tabla: %s", name)
        table.create(bind=engine)

app = FastAPI(title="API de Servicio de productos", version="1.0.0")

app.include_router(
    route_category.router,
    prefix="/category",
    tags=["Categories"],
    responses={404: {"description": "No encontrado"}},
)

app.include_router(
    route_products.router,
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "No encontrado"}},
)

app.include_router(
    route_variants.router,
    prefix="/variants",
    tags=["Products"],
    responses={404: {"description": "No encontrado"}},
)
