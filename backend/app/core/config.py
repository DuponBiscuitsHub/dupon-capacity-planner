from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Cargador de configuración via Pydantic BaseSettings.
    Lee y valida las variables desde el archivo .env local.
    En producción, las variables se inyectan desde GCP Secret Manager.
    """
    APP_NAME: str = "DCP Raw Material Planner"
    APP_ENV: str = "development"  # development | production

    # ── Base de Datos PostgreSQL ──────────────────────────────────────────────
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DATABASE_URL: str

    # ── Conexión JSON-RPC a Odoo ERP ──────────────────────────────────────────
    # ODOO_MODE=mock → usa datos de prueba sin conectar a Odoo (dev/CI)
    # ODOO_MODE=real → conecta a Odoo real (beta/producción)
    ODOO_MODE: str = "mock"
    ODOO_URL: str = ""
    ODOO_DB: str = ""
    ODOO_USER: str = ""
    ODOO_API_KEY: str = ""
    ODOO_TIMEOUT_SECONDS: int = 15

    # ── Seguridad JWT ─────────────────────────────────────────────────────────
    # CS-SECRETS-002: TTL reducido a 60 min. Usar RS256 en producción.
    # Generar secreto con: openssl rand -hex 32
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Sincronización con Odoo ───────────────────────────────────────────────
    # Intervalo en segundos (900 = 15 min)
    SYNC_INTERVAL_SECONDS: int = 900

    # Pydantic Settings: lee variables de entorno desde .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Singleton de configuración — importar con:
# from app.core.config import settings
settings = Settings()
