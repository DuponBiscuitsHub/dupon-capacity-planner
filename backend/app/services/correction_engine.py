"""
app/services/correction_engine.py — Motor de auto-calibración de factores de corrección.

Ejecutado después de cada sync exitoso por sync_worker.py.

Lógica:
  Para cada material con silo configurado:
    stock_expected = stock_ayer + entradas_hoy - consumo_teórico_hoy
    stock_actual   = stock.quant de Odoo (ya incluye ajuste sala de pasta → SSoT)
    consumo_real   = stock_ayer + entradas_hoy - stock_actual
    factor         = consumo_real / consumo_teórico   (1.0 si teórico == 0)

Invariantes:
  - Nunca escribe en Odoo.
  - Solo crea/actualiza registros del día actual (idempotente).
  - Si no hay datos suficientes (primer día), guarda factor=1.0.
  - El factor se guarda aunque sea 1.0 (para marcar que el día fue procesado).
"""
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.odoo_replica import PurchaseOrder, StockQuant
from app.models.planner import CorrectionFactor, SiloConfig

_logger = logging.getLogger("app.correction_engine")

# Límites de sanidad para el factor.
# Fuera de estos rangos, el dato es probablemente erróneo (ej. primer día,
# silo no mapeado, etc.) y se ignora para evitar contaminar el histórico.
_FACTOR_MIN = 0.50   # consumo 50% del teórico → mínimo plausible
_FACTOR_MAX = 2.00   # consumo 200% del teórico → máximo plausible


def run(db: Session, company_id: int) -> int:
    """Calcula y persiste el factor de corrección del día anterior.

    Se ejecuta tras el sync de la mañana (cuando ya tenemos el stock
    actualizado de Odoo, que incluye el ajuste de sala de pasta).

    Returns:
        Número de factores calculados/actualizados.
    """
    yesterday = date.today() - timedelta(days=1)
    _logger.info(
        "Running correction engine",
        extra={"date": str(yesterday), "company_id": company_id},
    )

    silos = db.query(SiloConfig).filter(SiloConfig.company_id == company_id).all()

    # Deduplicar por material_type: múltiples silos de harina (S-H1, S-H2, S-H3)
    # comparten material_type="harina", pero solo necesitamos un factor por material.
    # Usamos el primer silo mapeado a Odoo como representante.
    seen_materials: set[str] = set()
    unique_silos: list[SiloConfig] = []
    for silo in silos:
        if silo.material_type not in seen_materials:
            seen_materials.add(silo.material_type)
            unique_silos.append(silo)

    updated = 0

    for silo in unique_silos:
        factor = _calculate_factor(db, silo, yesterday, company_id)
        if factor is not None:
            _upsert_factor(db, yesterday, silo.material_type, company_id, factor)
            updated += 1

    db.commit()
    _logger.info(
        "Correction engine complete",
        extra={"date": str(yesterday), "updated": updated},
    )
    return updated


def _calculate_factor(
    db: Session,
    silo: SiloConfig,
    target_date: date,
    company_id: int,
) -> Optional[dict]:
    """Calcula el factor de corrección para un silo en una fecha.

    Returns None si no hay datos suficientes para calcular.
    Returns dict con factor y datos de trazabilidad.
    """
    if not silo.odoo_product_id or not silo.odoo_location_id:
        # TBD-3/TBD-4: silo sin mapear a Odoo, no se puede calcular
        _logger.debug(
            "Silo not mapped to Odoo — skipping",
            extra={"silo_code": silo.silo_code},
        )
        return None

    # Stock actual (post-ajuste sala de pasta, ya en Odoo)
    stock_actual_kg = _get_odoo_stock(db, silo)
    if stock_actual_kg is None:
        return None

    # Factor del día anterior para usar como stock_ayer (encadenado)
    # Si no existe, intentamos reconstruir desde la diferencia de stock.
    # En el primer día simplemente guardamos factor=1.0 sin trazabilidad completa.
    prev_factor_row = _get_factor_row(db, target_date - timedelta(days=1), silo.material_type, company_id)
    if prev_factor_row is None:
        # Sin histórico → guardamos factor=1.0 como baseline
        _logger.info(
            "No previous factor — saving baseline 1.0",
            extra={"silo_code": silo.silo_code, "date": str(target_date)},
        )
        return {
            "factor": 1.0,
            "stock_expected_kg": None,
            "stock_actual_kg": float(stock_actual_kg),
            "consumption_theoretical_kg": None,
            "consumption_actual_kg": None,
            "source": "auto",
        }

    stock_expected = float(prev_factor_row.stock_actual_kg or 0)

    # Entradas del día: POs recibidas para este material
    entries_kg = _get_day_entries(db, silo, target_date, company_id)

    # Consumo teórico: guardado en el factor del día anterior como referencia
    theoretical_kg = float(prev_factor_row.consumption_theoretical_kg or 0)

    stock_expected_today = stock_expected + entries_kg - theoretical_kg

    # consumo_real = lo que realmente ocurrió según Odoo
    consumption_actual = stock_expected + entries_kg - float(stock_actual_kg)

    if theoretical_kg <= 0:
        # Sin consumo teórico de referencia, usamos 1.0
        factor = 1.0
    else:
        factor = consumption_actual / theoretical_kg

    # Filtro de sanidad
    if not (_FACTOR_MIN <= factor <= _FACTOR_MAX):
        _logger.warning(
            "Factor out of sanity range — clamping to 1.0",
            extra={
                "silo_code": silo.silo_code,
                "factor": factor,
                "consumption_actual": consumption_actual,
                "theoretical_kg": theoretical_kg,
            },
        )
        factor = 1.0

    return {
        "factor": round(factor, 4),
        "stock_expected_kg": round(stock_expected_today, 2),
        "stock_actual_kg": round(float(stock_actual_kg), 2),
        "consumption_theoretical_kg": round(theoretical_kg, 2),
        "consumption_actual_kg": round(consumption_actual, 2),
        "source": "auto",
    }


def _get_odoo_stock(db: Session, silo: SiloConfig) -> Optional[float]:
    """Retorna el stock actual del silo desde stock_quants (ya incluye ajuste sala pasta)."""
    quant = db.query(StockQuant).filter(
        StockQuant.product_id == silo.odoo_product_id,
        StockQuant.location_id == silo.odoo_location_id,
    ).first()

    if quant is None:
        _logger.debug("No stock quant found", extra={"silo_code": silo.silo_code})
        return None

    return float(quant.quantity)


def _get_day_entries(
    db: Session,
    silo: SiloConfig,
    target_date: date,
    company_id: int,
) -> float:
    """Suma las entregas recibidas para este material en la fecha dada (POs done)."""
    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.product_id == silo.odoo_product_id,
        PurchaseOrder.company_id == company_id,
        PurchaseOrder.state == "done",
        PurchaseOrder.date_planned >= day_start,
        PurchaseOrder.date_planned < day_end,
    ).all()

    return sum(float(po.quantity) for po in pos)


def _get_factor_row(
    db: Session,
    target_date: date,
    material_type: str,
    company_id: int,
) -> Optional[CorrectionFactor]:
    """Busca un registro de factor de corrección para la fecha y material dados."""
    return db.query(CorrectionFactor).filter(
        CorrectionFactor.date == target_date,
        CorrectionFactor.material_type == material_type,
        CorrectionFactor.company_id == company_id,
    ).first()


def _upsert_factor(
    db: Session,
    target_date: date,
    material_type: str,
    company_id: int,
    data: dict,
) -> CorrectionFactor:
    """Crea o actualiza el factor de corrección para la fecha y material dados."""
    existing = _get_factor_row(db, target_date, material_type, company_id)

    if existing:
        existing.factor = data["factor"]
        existing.stock_expected_kg = data["stock_expected_kg"]
        existing.stock_actual_kg = data["stock_actual_kg"]
        existing.consumption_theoretical_kg = data["consumption_theoretical_kg"]
        existing.consumption_actual_kg = data["consumption_actual_kg"]
        existing.source = data["source"]
        existing.calculated_at = datetime.now(timezone.utc)
        return existing

    row = CorrectionFactor(
        date=target_date,
        material_type=material_type,
        company_id=company_id,
        factor=data["factor"],
        stock_expected_kg=data["stock_expected_kg"],
        stock_actual_kg=data["stock_actual_kg"],
        consumption_theoretical_kg=data["consumption_theoretical_kg"],
        consumption_actual_kg=data["consumption_actual_kg"],
        source=data["source"],
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(row)
    return row


def get_active_factor(db: Session, material_type: str, company_id: int) -> float:
    """Retorna el factor de corrección activo para usar en cálculos de entrega.

    Prioridad:
    1. Factor de hoy (si ya se calculó)
    2. Media de los últimos 10 días con datos
    3. 1.0 (sin corrección, sin histórico)

    Función pública usada por delivery_calculator.py.
    """
    today = date.today()

    # Factor de hoy
    today_row = _get_factor_row(db, today, material_type, company_id)
    if today_row:
        return float(today_row.factor)

    # Media últimos 10 días
    recent = db.query(CorrectionFactor).filter(
        CorrectionFactor.material_type == material_type,
        CorrectionFactor.company_id == company_id,
        CorrectionFactor.date >= today - timedelta(days=30),
        CorrectionFactor.source != "seeded",  # no contar valores baseline
    ).order_by(CorrectionFactor.date.desc()).limit(10).all()

    if recent:
        avg = sum(float(r.factor) for r in recent) / len(recent)
        _logger.debug(
            "Using average factor from history",
            extra={"material": material_type, "factor": avg, "n_days": len(recent)},
        )
        return round(avg, 4)

    return 1.0  # sin histórico → sin corrección
