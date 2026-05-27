import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

# ---------------------------------------------------------------------------
# Logging estructurado — nivel INFO en desarrollo, WARNING en producción.
# Permite reconstruir el flujo de ejecución sin depuración adicional.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dcp.backend")

# ---------------------------------------------------------------------------
# Aplicación FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Dupon Capacity Planner API",
    description="Operations analytical backend for the Dupon Capacity Planner (DCP).",
    version="1.0.0"
)

# ---------------------------------------------------------------------------
# CORS — solo orígenes explícitamente autorizados (CS-CORS-001).
# En producción, sustituir por la URL real del frontend en Cloud Run.
# NUNCA usar allow_origins=["*"] con allow_credentials=True.
# ---------------------------------------------------------------------------
_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Next.js dev server
    "http://127.0.0.1:3000",  # Alternativa local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def read_root():
    """
    Endpoint raíz — devuelve metadatos generales de la API.
    """
    return {
        "status": "online",
        "app": "Dupon Capacity Planner Backend",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check — verifica la conectividad con la base de datos.
    No expone detalles internos de SQLAlchemy al cliente (CS-LOGGING-001).
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        # El error se registra internamente con traza completa
        # pero NO se expone en la respuesta pública al cliente.
        logger.error(
            "Health check: fallo de conectividad con la base de datos. %s",
            e,
            exc_info=True,
        )
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
