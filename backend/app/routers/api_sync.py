"""
app/routers/api_sync.py — Endpoints de sincronización con Odoo.

POST /api/v1/sync/run    — Forzar sync manual (IT only)
GET  /api/v1/sync/status — Estado del último sync (user)
"""
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_auth, require_role
from app.models.planner import SyncLog
from app.services.sync_worker import sync_worker

_logger = logging.getLogger("app.sync")

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncStatus(BaseModel):
    model_name: str
    status: str
    records_synced: int
    synced_at: str
    error_message: str | None


class SyncRunResponse(BaseModel):
    message: str
    triggered_at: str


@router.post("/run", response_model=SyncRunResponse, status_code=status.HTTP_200_OK)
async def trigger_sync(
    current_user: dict = Depends(require_role("it")),
) -> SyncRunResponse:
    """Dispara un sync manual completo con Odoo y espera a que termine.

    Ejecuta en thread pool para no bloquear el event loop de uvicorn
    (el sync puede tardar 15-30s contra Odoo).
    Solo IT.
    """
    triggered_at = datetime.now(timezone.utc).isoformat()
    _logger.info("Manual sync triggered (sync)", extra={"by": current_user["username"]})
    await asyncio.get_running_loop().run_in_executor(
        None, sync_worker.run_once
    )
    _logger.info("Manual sync finished", extra={"by": current_user["username"]})
    return SyncRunResponse(message="Sync completed.", triggered_at=triggered_at)


@router.get("/status", response_model=list[SyncStatus])
def get_sync_status(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[SyncStatus]:
    """Retorna el resultado del último sync para cada modelo."""
    # Último registro por model_name
    logs = (
        db.query(SyncLog)
        .order_by(SyncLog.synced_at.desc())
        .limit(20)
        .all()
    )
    seen = set()
    result = []
    for log in logs:
        if log.model_name not in seen:
            seen.add(log.model_name)
            result.append(SyncStatus(
                model_name=log.model_name,
                status=log.status,
                records_synced=log.records_synced,
                synced_at=log.synced_at.isoformat(),
                error_message=log.error_message,
            ))
    return result


class LastSyncResponse(BaseModel):
    last_sync_at: str | None
    status: str  # success | failure | never


@router.get("/last", response_model=LastSyncResponse)
def get_last_sync(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> LastSyncResponse:
    """Retorna el timestamp del último sync exitoso (para mostrar en UI)."""
    last = (
        db.query(SyncLog)
        .filter(SyncLog.status == "success")
        .order_by(SyncLog.synced_at.desc())
        .first()
    )
    if not last:
        return LastSyncResponse(last_sync_at=None, status="never")
    return LastSyncResponse(
        last_sync_at=last.synced_at.isoformat(),
        status="success",
    )


# ── Health Check ──────────────────────────────────────────────────────────────

class OdooHealthResponse(BaseModel):
    odoo_reachable: bool
    latency_ms: int | None = None
    odoo_mode: str  # "mock" | "real"
    error: str | None = None


@router.get("/health", response_model=OdooHealthResponse)
async def check_odoo_health(
    current_user: dict = Depends(require_auth),
) -> OdooHealthResponse:
    """Verifica la conexión con Odoo sin sincronizar datos.

    Ejecuta authenticate() en thread pool (JSON-RPC síncrono).
    Retorna estado de conectividad y latencia.
    """
    if settings.ODOO_MODE == "mock":
        return OdooHealthResponse(
            odoo_reachable=True, odoo_mode="mock"
        )

    import time
    from app.core.odoo_client import OdooClient

    def _check() -> OdooHealthResponse:
        start = time.monotonic()
        try:
            client = OdooClient(
                base_url=settings.ODOO_URL,
                db=settings.ODOO_DB,
                user=settings.ODOO_USER,
                api_key=settings.ODOO_API_KEY,
            )
            client.authenticate()
            latency = int((time.monotonic() - start) * 1000)
            return OdooHealthResponse(
                odoo_reachable=True, latency_ms=latency, odoo_mode="real"
            )
        except Exception as exc:
            return OdooHealthResponse(
                odoo_reachable=False, odoo_mode="real",
                error=str(exc)[:200]
            )

    return await asyncio.get_running_loop().run_in_executor(None, _check)
