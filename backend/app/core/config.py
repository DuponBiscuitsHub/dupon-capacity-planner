from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application Settings loader using Pydantic BaseSettings.
    Loads and validates variables from the local .env file.
    """
    # Database Configuration
    DATABASE_URL: str
    
    # Odoo ERP XML-RPC Configuration
    ODOO_URL: str
    ODOO_DB: str
    ODOO_USER: str
    ODOO_API_KEY: str
    
    # Security Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Sync Configuration
    SYNC_INTERVAL_MINUTES: int = 30
    
    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate the settings singleton
settings = Settings()
