"""
app/main.py — FastAPI application entry point.

Solo: startup, lifespan, CORS, routers, health check.
Sin lógica de negocio. Sin queries directas a BD.
"""
import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.base import Base
# Importar todos los modelos para que Alembic los detecte
import app.models.odoo_replica  # noqa: F401
import app.models.planner       # noqa: F401
from app.services.sync_worker import sync_worker

# ── Logging ──────────────────────────────────────────────────────────────────

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "dcp.log")

os.makedirs(_LOG_DIR, exist_ok=True)

_root = logging.getLogger()
_root.setLevel(logging.INFO)

# Console handler (stdout → Cloud Logging en producción)
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter(_LOG_FORMAT))
_root.addHandler(_console)

# File handler (RotatingFileHandler → accesible desde admin)
_file = RotatingFileHandler(
    _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8",
)
_file.setFormatter(logging.Formatter(_LOG_FORMAT))
_root.addHandler(_file)

_logger = logging.getLogger("app")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.info(
        "Starting DCP Raw Material Planner — env=%s odoo_mode=%s",
        settings.APP_ENV,
        settings.ODOO_MODE,
    )

    # Inicializar BD SQLite en dev (strip schemas + create_all).
    # En producción (PostgreSQL) esta llamada es no-op.
    from app.core.database import _IS_SQLITE, _sqlite_init, _seed_companies_if_empty
    if _IS_SQLITE:
        _sqlite_init()
        _logger.info("SQLite dev DB initialized (schemas stripped, tables created)")
    else:
        # Safety net: asegurar que companies existe en PostgreSQL
        _seed_companies_if_empty()

    if settings.ODOO_MODE != "mock":
        _logger.info("Odoo sync enabled — interval=%ds", settings.SYNC_INTERVAL_SECONDS)
    else:
        _logger.warning("ODOO_MODE=mock — sync disabled. Set ODOO_MODE=real for production.")

    sync_worker.start()
    yield
    sync_worker.stop()
    _logger.info("DCP shutdown complete.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DCP Raw Material Planner API",
    description="Planificador de entregas de primera materia galleta (Dupon).",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

from app.routers.api_auth import router as auth_router
from app.routers.api_silos import router as silos_router
from app.routers.api_config import router as config_router
from app.routers.api_sync import router as sync_router
from app.routers.api_users import router as users_router
from app.routers.api_corrections import router as corrections_router
from app.routers.api_delivery_planning import router as planning_router
from app.routers.api_admin import router as admin_router

app.include_router(auth_router)
app.include_router(silos_router)
app.include_router(config_router)
app.include_router(sync_router)
app.include_router(users_router)
app.include_router(corrections_router)
app.include_router(planning_router)
app.include_router(admin_router)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["status"])
def health():
    """Liveness probe. Verifica conectividad a la BD."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "env": settings.APP_ENV, "odoo_mode": settings.ODOO_MODE}
    except Exception as exc:
        _logger.error("Health check DB failed: %s", exc)
        return {"status": "unhealthy", "detail": "database unreachable"}
