"""Conexión síncrona a la base de datos usando SQLAlchemy y proporciona sesiones por solicitud."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está definida en el archivo .env")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# al final de database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
