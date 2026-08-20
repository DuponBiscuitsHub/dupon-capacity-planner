"""
app/routers/api_silos.py — Endpoints de silos y entregas.

GET  /api/v1/silos              — Estado de todos los silos con autonomía
GET  /api/v1/deliveries         — Lista de sugerencias de entrega
POST /api/v1/deliveries/recalculate — Botón "Recalcular Entregas"
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_auth, validate_company_access
from app.models.odoo_replica import StockQuant
from app.models.planner import DeliverySuggestion, SiloConfig
from app.services.delivery_calculator import recalculate_deliveries
from app.services.consumption import corrected_hourly_consumption
from app.services.stock_projection import project_stock

_logger = logging.getLogger("app.silos")

router = APIRouter(prefix="/api/v1", tags=["silos"])


class SiloStatus(BaseModel):
    silo_code: str
    name: str
    material_type: str
    capacity_kg: float
    current_stock_kg: float | None
    fill_pct: float | None
    autonomy_hours: float | None  # horas hasta safety_stock según consumo actual
    status: str  # ok | warning | critical | unknown


class DeliverySuggestionOut(BaseModel):
    id: int
    silo_code: str
    material_type: str
    suggested_date: str
    qty_kg: float
    status: str
    po_name: str | None
    po_state: str | None


# ── Silos ─────────────────────────────────────────────────────────────────────

@router.get("/silos", response_model=list[SiloStatus])
def get_silos(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[SiloStatus]:
    """Retorna el estado actual de todos los silos de la planta."""
    validate_company_access(company_id, current_user)
    silos = db.query(SiloConfig).filter(SiloConfig.company_id == company_id).all()
    return [_build_silo_status(db, silo) for silo in silos]


def _build_silo_status(db: Session, silo: SiloConfig) -> SiloStatus:
    # Estrategia de lookup de stock:
    # 1. Si odoo_location_id configurado → filtro exacto por ubicación Odoo
    # 2. Fallback dev/mock → location_id = silo.id (seed antiguo)
    quant = None
    if silo.odoo_location_id:
        # La ubicación del silo identifica unívocamente el producto; no necesitamos
        # filtrar por product_id porque cada silo tiene 1 solo material.
        quant = db.query(StockQuant).filter(
            StockQuant.location_id == silo.odoo_location_id,
        ).first()
    else:
        # Fallback: buscar cualquier quant cuyo location_id coincide con el silo.id
        quant = db.query(StockQuant).filter(
            StockQuant.location_id == silo.id,
        ).first()

    stock_kg = float(quant.quantity) if quant else None

    capacity = float(silo.capacity_kg)
    safety = float(silo.safety_stock_kg)

    fill_pct = round((stock_kg / capacity) * 100, 1) if stock_kg is not None and capacity > 0 else None

    autonomy_hours = None
    silo_status = "unknown"
    if stock_kg is not None:
        if fill_pct is not None and fill_pct < 20:
            silo_status = "critical"
        elif fill_pct is not None and fill_pct < 40:
            silo_status = "warning"
        else:
            silo_status = "ok"

        # Horas hasta safety_stock según consumo corregido actual
        consumption_kg_h = corrected_hourly_consumption(db, silo, silo.company_id)
        if consumption_kg_h > 0:
            usable_stock = stock_kg - safety
            autonomy_hours = round(max(usable_stock, 0.0) / consumption_kg_h, 1)

    return SiloStatus(
        silo_code=silo.silo_code,
        name=silo.name,
        material_type=silo.material_type,
        capacity_kg=capacity,
        current_stock_kg=stock_kg,
        fill_pct=fill_pct,
        autonomy_hours=autonomy_hours,
        status=silo_status,
    )


# ── Proyección ────────────────────────────────────────────────────────────────

@router.get("/silos/projection")
def get_stock_projection(
    company_id: int = 1,
    days: int = 14,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Proyección de stock a N días para todos los silos."""
    validate_company_access(company_id, current_user)
    clamped_days = max(1, min(days, 30))
    return project_stock(db, company_id, clamped_days)


# ── Entregas ──────────────────────────────────────────────────────────────────

@router.get("/deliveries", response_model=list[DeliverySuggestionOut])
def get_deliveries(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[DeliverySuggestionOut]:
    """Lista todas las sugerencias de entrega activas, ordenadas por fecha."""
    validate_company_access(company_id, current_user)
    suggestions = (
        db.query(DeliverySuggestion)
        .filter(
            DeliverySuggestion.company_id == company_id,
            DeliverySuggestion.status != "delivered",
        )
        .order_by(DeliverySuggestion.suggested_date.asc())
        .all()
    )
    return [
        DeliverySuggestionOut(
            id=s.id,
            silo_code=s.silo_code,
            material_type=s.material_type,
            suggested_date=s.suggested_date.isoformat(),
            qty_kg=float(s.qty_kg),
            status=s.status,
            po_name=s.po_name,
            po_state=s.po_state,
        )
        for s in suggestions
    ]


@router.post("/deliveries/recalculate", response_model=list[DeliverySuggestionOut])
def trigger_recalculate(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[DeliverySuggestionOut]:
    """Dispara el recálculo de sugerencias de entrega.

    No toca entregas con status='confirmed' (bloqueadas por PO confirmada).
    """
    validate_company_access(company_id, current_user)
    _logger.info(
        "Recalculate triggered",
        extra={"triggered_by": current_user["username"], "company_id": company_id},
    )
    results = recalculate_deliveries(db, company_id)
    return [DeliverySuggestionOut(**r) for r in results]
