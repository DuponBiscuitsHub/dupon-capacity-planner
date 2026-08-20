"""
app/routers/api_delivery_planning.py — Endpoints de planificación de entregas.

GET  /api/v1/delivery-planning          — Tabla semáforo de POs
POST /api/v1/delivery-planning/update-date — Escribe date_planned en Odoo
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.odoo_client import OdooClient
from app.core.security import require_auth, require_role
from app.models.odoo_replica import PurchaseOrder
from app.services.delivery_planning import get_delivery_plan

_logger = logging.getLogger("app.delivery_planning_api")

router = APIRouter(prefix="/api/v1/delivery-planning", tags=["delivery-planning"])


class UpdateDateRequest(BaseModel):
    po_line_odoo_id: int
    new_date: str  # ISO 8601


class UpdateDateResponse(BaseModel):
    success: bool
    warning: str | None = None
    new_date_planned: str


@router.get("")
def get_plan(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Tabla de planificación de entregas con semáforo."""
    return get_delivery_plan(db, company_id)


@router.post("/update-date", response_model=UpdateDateResponse)
def update_po_date(
    body: UpdateDateRequest,
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> UpdateDateResponse:
    """Escribe date_planned en una PO line de Odoo.

    Restricciones:
    - state=done/cancel → 403 Forbidden
    - state=purchase → escribe pero retorna warning
    - state=draft/sent → escribe sin warning
    - ODOO_MODE=mock → no escribe, simula éxito
    """
    # Buscar la PO line en nuestra cache
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.odoo_id == body.po_line_odoo_id,
    ).first()

    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PO line {body.po_line_odoo_id} not found.",
        )

    # Validar estado
    if po.state in ("done", "cancel"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot edit PO in state '{po.state}'.",
        )

    # Parsear nueva fecha — Python 3.10 no acepta 'Z' en fromisoformat
    try:
        # Normalizar: "2026-07-20T15:00:00.000Z" → "2026-07-20T15:00:00+00:00"
        normalized = body.new_date.replace("Z", "+00:00")
        new_dt = datetime.fromisoformat(normalized)
        # Convertir a UTC naive para almacenar y enviar a Odoo
        if new_dt.tzinfo is not None:
            new_dt = new_dt.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format '{body.new_date}'. Use ISO 8601.",
        )

    warning = None
    if po.state == "purchase":
        warning = "poEditWarningConfirmed"

    # Escribir en Odoo (o mock)
    if settings.ODOO_MODE == "real":
        client = OdooClient(
            base_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            user=settings.ODOO_USER,
            api_key=settings.ODOO_API_KEY,
        )
        # Odoo espera datetime como string 'YYYY-MM-DD HH:MM:SS'
        odoo_date_str = new_dt.strftime("%Y-%m-%d %H:%M:%S")
        client.write(
            model="purchase.order.line",
            ids=[body.po_line_odoo_id],
            vals={"date_planned": odoo_date_str},
        )
        _logger.info(
            "PO date updated in Odoo",
            extra={
                "po_line_odoo_id": body.po_line_odoo_id,
                "new_date": odoo_date_str,
                "by": current_user["username"],
            },
        )
    else:
        _logger.info(
            "PO date update MOCK (skipped Odoo write)",
            extra={"po_line_odoo_id": body.po_line_odoo_id},
        )

    # Actualizar cache local
    po.date_planned = new_dt
    db.commit()

    return UpdateDateResponse(
        success=True,
        warning=warning,
        new_date_planned=new_dt.isoformat(),
    )
