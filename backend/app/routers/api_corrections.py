"""
app/routers/api_corrections.py — Endpoints de factores de corrección y tabla CON.

Propósito:
  - Consultar el histórico de factores de corrección (para transparencia y auditoría)
  - Ver el factor activo actual por material
  - Gestionar la tabla CON (ref_consumption_rates) — solo IT
  - Gestionar line_formats — solo IT

Reglas:
  - Solo lectura para rol 'user'
  - IT puede editar ref_consumption_rates y line_formats
  - Nunca se escriben factores manualmente (son auto-calculados por correction_engine)
"""
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_auth, require_role
from app.models.planner import CorrectionFactor, LineFormat, RefConsumptionRate
from app.services.correction_engine import get_active_factor

_logger = logging.getLogger("app.api_corrections")

router = APIRouter(prefix="/api/v1", tags=["corrections"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class CorrectionFactorOut(BaseModel):
    id: int
    date: date
    material_type: str
    factor: float
    stock_expected_kg: float | None
    stock_actual_kg: float | None
    consumption_theoretical_kg: float | None
    consumption_actual_kg: float | None
    source: str

    class Config:
        from_attributes = True


class ActiveFactorOut(BaseModel):
    material_type: str
    factor: float
    company_id: int


class RefRateOut(BaseModel):
    id: int
    format_code: str
    material_type: str
    kg_per_day: float
    company_id: int

    class Config:
        from_attributes = True


class RefRateUpdate(BaseModel):
    kg_per_day: float = Field(..., gt=0, description="kg por máquina por día (24h)")


class RefRateCreate(BaseModel):
    format_code: str = Field(..., min_length=2, max_length=32)
    material_type: str = Field(..., min_length=2, max_length=32)
    kg_per_day: float = Field(..., gt=0)
    company_id: int = Field(default=1)


class LineFormatOut(BaseModel):
    id: int
    line_code: str
    format_code: str
    machines: int
    company_id: int

    class Config:
        from_attributes = True


class LineFormatUpdate(BaseModel):
    machines: int = Field(..., gt=0, le=20, description="Nº máquinas de la línea")


# ── Endpoints — Factores de corrección ───────────────────────────────────────

@router.get("/corrections", response_model=list[CorrectionFactorOut])
def list_corrections(
    days: int = 30,
    material_type: str | None = None,
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    """Retorna el histórico de factores de corrección.

    Parámetros:
      days: número de días hacia atrás (default 30)
      material_type: filtro por material (harina, azucar, aceite)
    """
    since = date.today() - timedelta(days=days)
    query = db.query(CorrectionFactor).filter(CorrectionFactor.date >= since)

    if material_type:
        query = query.filter(CorrectionFactor.material_type == material_type)

    rows = query.order_by(CorrectionFactor.date.desc()).all()
    return [
        CorrectionFactorOut(
            id=r.id,
            date=r.date,
            material_type=r.material_type,
            factor=float(r.factor),
            stock_expected_kg=float(r.stock_expected_kg) if r.stock_expected_kg else None,
            stock_actual_kg=float(r.stock_actual_kg) if r.stock_actual_kg else None,
            consumption_theoretical_kg=float(r.consumption_theoretical_kg) if r.consumption_theoretical_kg else None,
            consumption_actual_kg=float(r.consumption_actual_kg) if r.consumption_actual_kg else None,
            source=r.source,
        )
        for r in rows
    ]


@router.get("/corrections/current", response_model=list[ActiveFactorOut])
def get_current_factors(
    company_id: int = 1,
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    """Retorna el factor de corrección activo para cada material.

    Usado por el dashboard para mostrar el indicador de desviación.
    """
    materials = ["harina", "azucar", "aceite"]
    return [
        ActiveFactorOut(
            material_type=m,
            factor=get_active_factor(db, m, company_id),
            company_id=company_id,
        )
        for m in materials
    ]


# ── Endpoints — Tabla de referencia CON ───────────────────────────────────────

@router.get("/config/recipes", response_model=list[RefRateOut])
def list_recipes(
    company_id: int = 1,
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    """Lista todos los consumos de referencia (tabla CON).

    Devuelve ~170 filas: formato × material → kg/día por máquina.
    """
    rows = db.query(RefConsumptionRate).filter(
        RefConsumptionRate.company_id == company_id
    ).order_by(RefConsumptionRate.format_code, RefConsumptionRate.material_type).all()
    return [
        RefRateOut(
            id=r.id,
            format_code=r.format_code,
            material_type=r.material_type,
            kg_per_day=float(r.kg_per_day),
            company_id=r.company_id,
        )
        for r in rows
    ]


@router.put("/config/recipes/{recipe_id}", response_model=RefRateOut)
def update_recipe_rate(
    recipe_id: int,
    body: RefRateUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("it")),
):
    """Actualiza el kg/día de un consumo de referencia (solo IT).

    Permite ajustar los valores si la realidad de planta cambia.
    """
    row = db.query(RefConsumptionRate).filter(RefConsumptionRate.id == recipe_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe rate not found")

    old_value = float(row.kg_per_day)
    row.kg_per_day = body.kg_per_day
    row.updated_by = user["user_id"]
    db.commit()
    db.refresh(row)
    _logger.info(
        "RefConsumptionRate updated",
        extra={
            "id": recipe_id,
            "format": row.format_code,
            "material": row.material_type,
            "old_kg_per_day": old_value,
            "new_kg_per_day": body.kg_per_day,
            "updated_by": user["user_id"],
        },
    )
    return RefRateOut(
        id=row.id,
        format_code=row.format_code,
        material_type=row.material_type,
        kg_per_day=float(row.kg_per_day),
        company_id=row.company_id,
    )


@router.post("/config/recipes", response_model=RefRateOut, status_code=status.HTTP_201_CREATED)
def create_recipe_rate(
    body: RefRateCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("it")),
):
    """Crea un nuevo consumo de referencia (solo IT).

    Usado cuando se introduce un nuevo formato o ingrediente.
    """
    # Verificar duplicado
    existing = db.query(RefConsumptionRate).filter(
        RefConsumptionRate.format_code == body.format_code,
        RefConsumptionRate.material_type == body.material_type,
        RefConsumptionRate.company_id == body.company_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rate already exists for {body.format_code}/{body.material_type}",
        )

    row = RefConsumptionRate(
        format_code=body.format_code,
        material_type=body.material_type,
        kg_per_day=body.kg_per_day,
        company_id=body.company_id,
        updated_by=user["user_id"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    _logger.info(
        "RefConsumptionRate created",
        extra={
            "id": row.id,
            "format": row.format_code,
            "material": row.material_type,
            "kg_per_day": body.kg_per_day,
            "created_by": user["user_id"],
        },
    )
    return RefRateOut(
        id=row.id,
        format_code=row.format_code,
        material_type=row.material_type,
        kg_per_day=float(row.kg_per_day),
        company_id=row.company_id,
    )


@router.delete("/config/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_rate(
    recipe_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_role("it")),
):
    """Elimina un consumo de referencia (solo IT)."""
    row = db.query(RefConsumptionRate).filter(RefConsumptionRate.id == recipe_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe rate not found")

    _logger.info(
        "RefConsumptionRate deleted",
        extra={"id": recipe_id, "format": row.format_code, "material": row.material_type},
    )
    db.delete(row)
    db.commit()


# ── Endpoints — Line Formats ─────────────────────────────────────────────────

@router.get("/config/line-formats", response_model=list[LineFormatOut])
def list_line_formats(
    company_id: int = 1,
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    """Lista todos los mappings línea → formato con nº de máquinas."""
    rows = db.query(LineFormat).filter(
        LineFormat.company_id == company_id
    ).order_by(LineFormat.line_code, LineFormat.format_code).all()
    return [
        LineFormatOut(
            id=r.id,
            line_code=r.line_code,
            format_code=r.format_code,
            machines=r.machines,
            company_id=r.company_id,
        )
        for r in rows
    ]


@router.put("/config/line-formats/{lf_id}", response_model=LineFormatOut)
def update_line_format(
    lf_id: int,
    body: LineFormatUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("it")),
):
    """Actualiza el nº de máquinas de un mapping línea → formato (solo IT)."""
    row = db.query(LineFormat).filter(LineFormat.id == lf_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line format not found")

    row.machines = body.machines
    db.commit()
    db.refresh(row)
    _logger.info(
        "LineFormat updated",
        extra={"id": lf_id, "line": row.line_code, "format": row.format_code, "machines": body.machines},
    )
    return LineFormatOut(
        id=row.id,
        line_code=row.line_code,
        format_code=row.format_code,
        machines=row.machines,
        company_id=row.company_id,
    )
