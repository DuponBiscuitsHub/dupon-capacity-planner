from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Cargador de configuración via Pydantic BaseSettings.
    Lee y valida las variables desde el archivo .env local.
    En producción, las variables se inyectan desde GCP Secret Manager.
    """
    # -------------------------------------------------------------------------
    # Base de Datos PostgreSQL
    # -------------------------------------------------------------------------
    DB_USER: str
    DB_PASSWORD: str
    DATABASE_URL: str

    # -------------------------------------------------------------------------
    # Conexión XML-RPC a Odoo ERP
    # -------------------------------------------------------------------------
    ODOO_URL: str
    ODOO_DB: str
    ODOO_USER: str
    ODOO_API_KEY: str

    # -------------------------------------------------------------------------
    # Seguridad JWT
    # CS-SECRETS-002: TTL reducido a 60 min (24h es excesivo para datos industriales).
    # Para producción, migrar a RS256 con par de claves asimétrico según architecture_plan.md §6.2.
    # El JWT_SECRET debe generarse con: openssl rand -hex 32 (256 bits mínimo).
    # -------------------------------------------------------------------------
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 24h → 60 min (CS-SECRETS-002)

    # -------------------------------------------------------------------------
    # Motor de Sincronización Odoo
    # -------------------------------------------------------------------------
    SYNC_INTERVAL_MINUTES: int = 30

    # Pydantic Settings: lee variables de entorno desde .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Singleton de configuración — importar desde cualquier módulo con:
# from app.core.config import settings
settings = Settings()

