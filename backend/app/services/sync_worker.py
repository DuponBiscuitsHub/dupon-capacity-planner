"""
app/services/sync_worker.py — Worker background de sincronización con Odoo.

Ejecuta el sync periódico cada SYNC_INTERVAL_SECONDS.
Puede también dispararse manualmente vía POST /api/v1/sync/run.

Paradigma: OOP — tiene estado propio (is_running, _task).
"""
import asyncio
import logging

from app.core.config import settings
from app.core.database import SessionLocal

_logger = logging.getLogger("app.sync_worker")


class SyncWorker:
    """Worker background asyncio para el sync periódico con Odoo.

    Lifecycle (lifespan de FastAPI):
      sync_worker.start()  — startup
      sync_worker.stop()   — shutdown
    """

    def __init__(self) -> None:
        self.is_running: bool = False
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._sync_loop())
        _logger.info(
            "SyncWorker started (interval=%ds, mode=%s)",
            settings.SYNC_INTERVAL_SECONDS,
            settings.ODOO_MODE,
        )

    def stop(self) -> None:
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        _logger.info("SyncWorker stopped.")

    async def _sync_loop(self) -> None:
        """Bucle principal: espera el intervalo y lanza sync en thread pool."""
        while self.is_running:
            try:
                await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
                await asyncio.get_running_loop().run_in_executor(None, _run_sync)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _logger.exception("Unexpected error in sync loop: %s", exc)
                await asyncio.sleep(30)  # Backoff breve antes de reintentar

    def run_once(self) -> None:
        """Ejecuta un ciclo de sync completo (síncrono, para background tasks)."""
        _run_sync()


# Singleton — importar como: from app.services.sync_worker import sync_worker
sync_worker = SyncWorker()


def _run_sync() -> None:
    """Ejecuta el sync engine completo y luego actualiza factores de corrección."""
    from app.core.sync_engine import OdooSyncEngine
    from app.services import correction_engine
    from app.models.planner import Company

    db = SessionLocal()
    try:
        engine = OdooSyncEngine(db)
        engine.run_full_sync()

        # Tras el sync, calcular factores de corrección para cada compañía activa
        companies = db.query(Company).filter(Company.is_active.is_(True)).all()
        if companies:
            for company in companies:
                correction_engine.run(db, company_id=company.id)
        else:
            # Fallback si no hay tabla companies poblada (dev sin seed)
            correction_engine.run(db, company_id=1)

    except Exception as exc:
        _logger.exception("Sync failed: %s", exc)
    finally:
        db.close()

