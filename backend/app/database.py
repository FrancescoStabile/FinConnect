"""
Configurazione SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from app.config import get_settings

settings = get_settings()

# Crea l'engine SQLAlchemy (sync)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verifica connessione prima dell'uso
)

# SessionLocal factory per creare sessioni DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class per i modelli ORM
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency che fornisce una sessione database.
    Chiude automaticamente la sessione al termine della request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
