"""
app/services/consumption.py — Cálculo unificado de consumo por silo.

Función única que calcula el consumo teórico corregido para un silo,
reutilizable por delivery_calculator (kg/h) y stock_projection (kg/día).

Paradigma: Funcional — sin estado.
"""
import logging

from sqlalchemy.orm import Session

from app.models.planner import LineFormat, RefConsumptionRate, SiloConfig
from app.services import correction_engine

_logger = logging.getLogger("app.consumption")


def corrected_daily_consumption(
    db: Session, silo: SiloConfig, company_id: int
) -> float:
    """Consumo diario corregido en kg/día para un silo.

    Flujo:
      1. Por cada línea activa (LineFormat):
         consumo_linea = kg_per_day × machines
      2. Suma total = Σ consumo_linea
      3. Aplica factor de corrección histórico

    Returns:
        Consumo en kg/día (corregido). 0.0 si no hay datos.
    """
    line_formats = db.query(LineFormat).filter(
        LineFormat.company_id == company_id,
    ).all()

    if not line_formats:
        _logger.debug(
            "No line_formats configured",
            extra={"silo_code": silo.silo_code, "company_id": company_id},
        )
        return 0.0

    total_kg_day = 0.0
    for lf in line_formats:
        rate = db.query(RefConsumptionRate).filter(
            RefConsumptionRate.format_code == lf.format_code,
            RefConsumptionRate.material_type == silo.material_type,
            RefConsumptionRate.company_id == company_id,
        ).first()

        if not rate or float(rate.kg_per_day) <= 0:
            continue

        total_kg_day += float(rate.kg_per_day) * lf.machines

    if total_kg_day <= 0:
        return 0.0

    factor = correction_engine.get_active_factor(
        db, silo.material_type, company_id,
    )
    corrected = total_kg_day * factor

    _logger.debug(
        "Daily consumption calculated",
        extra={
            "silo_code": silo.silo_code,
            "theoretical_kg_day": total_kg_day,
            "factor": factor,
            "corrected_kg_day": corrected,
        },
    )
    return corrected


def corrected_hourly_consumption(
    db: Session, silo: SiloConfig, company_id: int
) -> float:
    """Consumo horario corregido en kg/h. Wrapper sobre daily / 24."""
    return corrected_daily_consumption(db, silo, company_id) / 24.0
