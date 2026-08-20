"""
app/routers/api_config.py — Endpoints de configuración (líneas y silos).

GET /api/v1/config/lines         — Lista líneas con capacidad teórica (user)
PUT /api/v1/config/lines/{code}  — Actualizar capacidad de una línea (IT only)
GET /api/v1/config/silos         — Lista configuración de silos (user)
PUT /api/v1/config/silos/{id}    — Actualizar silo (IT only)
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_auth, require_role, validate_company_access
from app.models.odoo_replica import MrpProduction, Workcenter
from app.models.planner import LineCapacity, SiloConfig

_logger = logging.getLogger("app.config")

router = APIRouter(prefix="/api/v1/config", tags=["config"])


class LineCapacityOut(BaseModel):
    line_code: str
    capacity_kg_h: float
    is_active: bool  # True si hay MO activa en esta línea
    company_id: int


class LineCapacityUpdate(BaseModel):
    capacity_kg_h: float = Field(..., gt=0, le=10000)


class SiloConfigOut(BaseModel):
    id: int
    silo_code: str
    name: str
    material_type: str
    capacity_kg: float
    safety_stock_kg: float
    company_id: int


class SiloConfigUpdate(BaseModel):
    safety_stock_kg: float = Field(..., ge=0)
    capacity_kg: float = Field(..., gt=0)


# ── Líneas ────────────────────────────────────────────────────────────────────

@router.get("/lines", response_model=list[LineCapacityOut])
def get_lines(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[LineCapacityOut]:
    """Lista todas las líneas con su capacidad configurada y si están activas."""
    validate_company_access(company_id, current_user)
    lines = (
        db.query(LineCapacity)
        .filter(LineCapacity.company_id == company_id)
        .order_by(LineCapacity.line_code)
        .all()
    )

    # MOs activas para marcar qué líneas están produciendo
    active_workcenter_codes = _get_active_workcenter_codes(db, company_id)

    return [
        LineCapacityOut(
            line_code=lc.line_code,
            capacity_kg_h=float(lc.capacity_kg_h),
            is_active=lc.line_code in active_workcenter_codes,
            company_id=lc.company_id,
        )
        for lc in lines
    ]


@router.put("/lines/{line_code}", response_model=LineCapacityOut)
def update_line_capacity(
    line_code: str,
    body: LineCapacityUpdate,
    company_id: int = 1,
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> LineCapacityOut:
    """Actualiza la capacidad teórica de una línea. Solo IT."""
    line = db.query(LineCapacity).filter(
        LineCapacity.line_code == line_code.upper(),
        LineCapacity.company_id == company_id,
    ).first()
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found.")

    line.capacity_kg_h = body.capacity_kg_h
    line.updated_by = current_user["user_id"]
    db.commit()

    _logger.info(
        "Line capacity updated",
        extra={"line_code": line_code, "new_capacity": body.capacity_kg_h, "by": current_user["username"]},
    )
    active_codes = _get_active_workcenter_codes(db, company_id)
    return LineCapacityOut(
        line_code=line.line_code,
        capacity_kg_h=float(line.capacity_kg_h),
        is_active=line.line_code in active_codes,
        company_id=line.company_id,
    )


# ── Silos ─────────────────────────────────────────────────────────────────────

@router.get("/silos", response_model=list[SiloConfigOut])
def get_silo_configs(
    company_id: int = 1,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[SiloConfigOut]:
    """Lista la configuración de todos los silos."""
    validate_company_access(company_id, current_user)
    silos = db.query(SiloConfig).filter(SiloConfig.company_id == company_id).all()
    return [
        SiloConfigOut(
            id=s.id,
            silo_code=s.silo_code,
            name=s.name,
            material_type=s.material_type,
            capacity_kg=float(s.capacity_kg),
            safety_stock_kg=float(s.safety_stock_kg),
            company_id=s.company_id,
        )
        for s in silos
    ]


@router.put("/silos/{silo_id}", response_model=SiloConfigOut)
def update_silo_config(
    silo_id: int,
    body: SiloConfigUpdate,
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> SiloConfigOut:
    """Actualiza capacidad y safety stock de un silo. Solo IT."""
    silo = db.query(SiloConfig).filter(SiloConfig.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Silo not found.")

    silo.capacity_kg = body.capacity_kg
    silo.safety_stock_kg = body.safety_stock_kg
    db.commit()

    _logger.info(
        "Silo config updated",
        extra={"silo_code": silo.silo_code, "by": current_user["username"]},
    )
    return SiloConfigOut(
        id=silo.id,
        silo_code=silo.silo_code,
        name=silo.name,
        material_type=silo.material_type,
        capacity_kg=float(silo.capacity_kg),
        safety_stock_kg=float(silo.safety_stock_kg),
        company_id=silo.company_id,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_active_workcenter_codes(db: Session, company_id: int) -> set[str]:
    """Retorna los códigos de workcenter con MOs activas."""
    active_ids = (
        db.query(MrpProduction.workcenter_id)
        .filter(
            MrpProduction.company_id == company_id,
            MrpProduction.state.in_(["confirmed", "progress"]),
            MrpProduction.workcenter_id.isnot(None),
        )
        .distinct()
        .all()
    )
    ids = [r[0] for r in active_ids]
    if not ids:
        return set()

    wcs = db.query(Workcenter.code).filter(Workcenter.odoo_id.in_(ids)).all()
    return {wc.code for wc in wcs if wc.code}
