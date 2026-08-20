"""
app/services/delivery_calculator.py — Motor de cálculo de ventanas de entrega.

Calcula cuándo y cuánto descargar en cada silo basándose en:
  - Stock actual (stock_quants de Odoo sincronizado)
  - Consumo proyectado (MOs activas × BOM × capacidad por línea)
  - POs existentes en Odoo para ese material

Paradigma: Funcional — sin estado entre llamadas.
Solo toca DeliverySuggestion con status != 'confirmed' (las confirmadas están bloqueadas).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

from sqlalchemy.orm import Session

from app.models.odoo_replica import PurchaseOrder, StockQuant
from app.models.planner import DeliverySuggestion, SiloConfig
from app.services.consumption import corrected_hourly_consumption

_logger = logging.getLogger("app.delivery_calculator")

# Margen de seguridad antes del safety_stock para la ventana de descarga (horas)
_SAFETY_MARGIN_HOURS = 4


class _SiloProjection(NamedTuple):
    silo: SiloConfig
    stock_kg: float
    consumption_kg_h: float
    hours_until_safety: float
    suggested_dt: datetime
    qty_to_order_kg: float


def recalculate_deliveries(db: Session, company_id: int) -> list[dict]:
    """Recalcula sugerencias de entrega para todos los silos de una planta.

    Solo actualiza sugerencias con status en ('draft', 'po_pending').
    Las entregas 'confirmed' permanecen intactas.

    Returns:
        Lista de sugerencias actualizadas (dict con los campos principales).
    """
    _logger.info("Starting delivery recalculation", extra={"company_id": company_id})

    silos = db.query(SiloConfig).filter(SiloConfig.company_id == company_id).all()
    if not silos:
        _logger.warning("No silos configured for company", extra={"company_id": company_id})
        return []

    projections = [
        p for silo in silos
        if (p := _project_silo(db, silo, company_id)) is not None
    ]

    results = []
    for proj in projections:
        suggestion = _upsert_suggestion(db, proj, company_id)
        results.append(_to_dict(suggestion))

    db.commit()
    _logger.info(
        "Delivery recalculation complete",
        extra={"company_id": company_id, "suggestions": len(results)},
    )
    return results


def _project_silo(
    db: Session, silo: SiloConfig, company_id: int
) -> _SiloProjection | None:
    """Calcula la proyección de consumo y ventana de descarga para un silo."""
    stock_kg = _get_silo_stock(db, silo)
    if stock_kg is None:
        _logger.warning(
            "No stock data for silo — skipping",
            extra={"silo_code": silo.silo_code},
        )
        return None

    consumption_kg_h = _calculate_consumption_rate(db, silo, company_id)
    if consumption_kg_h <= 0:
        _logger.info(
            "Zero consumption for silo (no active MOs?)",
            extra={"silo_code": silo.silo_code},
        )
        consumption_kg_h = 0.001  # evitar división por cero, autonomía muy larga

    usable_stock = stock_kg - float(silo.safety_stock_kg)
    hours_until_safety = max(0.0, usable_stock / consumption_kg_h) - _SAFETY_MARGIN_HOURS
    suggested_dt = datetime.now(timezone.utc) + timedelta(hours=max(0.0, hours_until_safety))

    # Cantidad óptima: rellenar hasta capacidad máxima descontando stock proyectado en la ventana
    projected_stock_at_delivery = max(
        0.0, stock_kg - (consumption_kg_h * max(0.0, hours_until_safety))
    )
    qty_to_order_kg = float(silo.capacity_kg) - projected_stock_at_delivery

    return _SiloProjection(
        silo=silo,
        stock_kg=stock_kg,
        consumption_kg_h=consumption_kg_h,
        hours_until_safety=hours_until_safety,
        suggested_dt=suggested_dt,
        qty_to_order_kg=max(0.0, qty_to_order_kg),
    )


def _get_silo_stock(db: Session, silo: SiloConfig) -> float | None:
    """Retorna el stock actual del silo en kg desde stock_quants."""
    if not silo.odoo_location_id or not silo.odoo_product_id:
        # TBD-3 / TBD-4: location_id y product_id pendientes de configurar
        return None

    quant = db.query(StockQuant).filter(
        StockQuant.product_id == silo.odoo_product_id,
        StockQuant.location_id == silo.odoo_location_id,
    ).first()

    return float(quant.quantity) if quant else 0.0


def _calculate_consumption_rate(
    db: Session, silo: SiloConfig, company_id: int
) -> float:
    """Consumo horario CORREGIDO del material del silo.

    Delegado a app.services.consumption (SSoT).
    """
    return corrected_hourly_consumption(db, silo, company_id)




def _upsert_suggestion(
    db: Session, proj: _SiloProjection, company_id: int
) -> DeliverySuggestion:
    """Crea o actualiza la sugerencia de entrega para el silo.

    Nunca toca registros con status='confirmed'.
    """
    existing = db.query(DeliverySuggestion).filter(
        DeliverySuggestion.silo_code == proj.silo.silo_code,
        DeliverySuggestion.company_id == company_id,
        DeliverySuggestion.status != "confirmed",  # 🔒 No tocar confirmadas
        DeliverySuggestion.status != "delivered",
    ).first()

    # Buscar si hay PO en Odoo para este material
    po = _find_matching_po(db, proj, company_id)
    new_status = "po_pending" if po else "draft"

    if existing:
        existing.suggested_date = proj.suggested_dt
        existing.qty_kg = proj.qty_to_order_kg
        existing.status = new_status
        existing.po_odoo_id = po.odoo_id if po else None
        existing.po_name = po.name if po else None
        existing.po_state = po.state if po else None
        existing.updated_at = datetime.now(timezone.utc)
        return existing

    suggestion = DeliverySuggestion(
        silo_code=proj.silo.silo_code,
        material_type=proj.silo.material_type,
        suggested_date=proj.suggested_dt,
        qty_kg=proj.qty_to_order_kg,
        status=new_status,
        po_odoo_id=po.odoo_id if po else None,
        po_name=po.name if po else None,
        po_state=po.state if po else None,
        company_id=company_id,
    )
    db.add(suggestion)
    return suggestion


def _find_matching_po(
    db: Session, proj: _SiloProjection, company_id: int
) -> PurchaseOrder | None:
    """Busca una PO abierta para el material del silo con fecha cercana."""
    if not proj.silo.odoo_product_id:
        return None

    window_start = proj.suggested_dt - timedelta(days=3)
    window_end = proj.suggested_dt + timedelta(days=3)

    return db.query(PurchaseOrder).filter(
        PurchaseOrder.product_id == proj.silo.odoo_product_id,
        PurchaseOrder.company_id == company_id,
        PurchaseOrder.state.in_(["draft", "purchase"]),
        PurchaseOrder.date_planned.between(window_start, window_end),
    ).first()


def _to_dict(suggestion: DeliverySuggestion) -> dict:
    """Serializa una DeliverySuggestion a dict para la respuesta API."""
    return {
        "id": suggestion.id,
        "silo_code": suggestion.silo_code,
        "material_type": suggestion.material_type,
        "suggested_date": suggestion.suggested_date.isoformat(),
        "qty_kg": float(suggestion.qty_kg),
        "status": suggestion.status,
        "po_name": suggestion.po_name,
        "po_state": suggestion.po_state,
    }
