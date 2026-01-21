"""
Configurazione applicazione.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    
    # Database
    DATABASE_URL: str = "postgresql://finconnect:finconnect_secret@localhost:5432/finconnect"
    
    # JWT Authentication
    SECRET_KEY: str = "finconnect-dev-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 ore
    
    # App
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Restituisce l'istanza cached delle impostazioni."""
    return Settings()
