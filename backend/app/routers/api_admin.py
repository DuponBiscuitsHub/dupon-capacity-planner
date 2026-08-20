"""
app/routers/api_admin.py — Endpoints de administración (role=it).

GET /api/v1/admin/logs — Lectura de logs del servidor.
"""
import os
import logging
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.security import require_role

_logger = logging.getLogger("app.admin")

_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs", "dcp.log",
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class LogsResponse(BaseModel):
    lines: list[str]
    total_lines: int
    log_file: str


@router.get("/logs", response_model=LogsResponse)
def get_logs(
    lines: int = Query(default=200, ge=1, le=2000),
    level: str = Query(default="", description="Filter by level: INFO, WARNING, ERROR"),
    current_user: dict = Depends(require_role("it")),
) -> LogsResponse:
    """Lee las últimas N líneas del archivo de logs.

    Filtro opcional por nivel (INFO/WARNING/ERROR).
    Solo accesible con role 'it'.
    """
    if not os.path.exists(_LOG_FILE):
        return LogsResponse(lines=[], total_lines=0, log_file=_LOG_FILE)

    try:
        with open(_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cannot read log file: {exc}",
        ) from exc

    # Filtrar por nivel si se especifica
    if level:
        level_upper = level.upper()
        all_lines = [
            ln for ln in all_lines
            if f"[{level_upper}]" in ln
        ]

    # Últimas N líneas
    tail = list(deque(all_lines, maxlen=lines))

    return LogsResponse(
        lines=[ln.rstrip("\n") for ln in tail],
        total_lines=len(all_lines),
        log_file=_LOG_FILE,
    )
