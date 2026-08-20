"""
app/services/stock_projection.py — Proyección de stock forward-looking.

Calcula la evolución del stock por silo para los próximos N días,
basándose en stock actual, consumo teórico corregido y POs planificadas.

Paradigma: Funcional — sin estado entre llamadas.
"""
import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.odoo_replica import PurchaseOrder, StockQuant
from app.models.planner import SiloConfig
from app.services.consumption import corrected_daily_consumption

_logger = logging.getLogger("app.stock_projection")

_PROJECTION_DAYS = 14


def project_stock(
    db: Session, company_id: int, days: int = _PROJECTION_DAYS
) -> list[dict]:
    """Genera la proyección diaria de stock para todos los silos.

    Returns:
        [
          {
            "silo_code": "S-H1",
            "material_type": "harina",
            "capacity_kg": 25000,
            "safety_stock_kg": 5000,
            "points": [
              {"date": "2026-07-20", "stock_kg": 18000},
              {"date": "2026-07-21", "stock_kg": 16500},
              ...
            ],
            "po_events": [
              {"date": "2026-07-23", "qty_kg": 25000, "po_name": "PO00123"},
            ]
          }
        ]
    """
    silos = db.query(SiloConfig).filter(
        SiloConfig.company_id == company_id,
    ).all()
    if not silos:
        return []

    today = date.today()
    result = []

    for silo in silos:
        stock_kg = _get_stock(db, silo)
        if stock_kg is None:
            continue

        consumption_kg_day = _daily_consumption(db, silo, company_id)
        po_events = _get_po_events(db, silo, company_id, today, days)

        points = _simulate(stock_kg, consumption_kg_day, po_events,
                           float(silo.capacity_kg), today, days)

        result.append({
            "silo_code": silo.silo_code,
            "material_type": silo.material_type,
            "capacity_kg": float(silo.capacity_kg),
            "safety_stock_kg": float(silo.safety_stock_kg),
            "consumption_kg_day": round(consumption_kg_day, 1),
            "points": points,
            "po_events": po_events,
        })

    return result


def _get_stock(db: Session, silo: SiloConfig) -> float | None:
    """Stock actual del silo en kg."""
    if not silo.odoo_location_id:
        return None
    quant = db.query(StockQuant).filter(
        StockQuant.location_id == silo.odoo_location_id,
    ).first()
    return float(quant.quantity) if quant else 0.0


def _daily_consumption(
    db: Session, silo: SiloConfig, company_id: int
) -> float:
    """Consumo diario en kg (corregido). Delegado a consumption.py (SSoT)."""
    return corrected_daily_consumption(db, silo, company_id)


def _get_po_events(
    db: Session, silo: SiloConfig, company_id: int,
    start: date, days: int,
) -> list[dict]:
    """POs planificadas para este silo dentro del rango de proyección."""
    if not silo.odoo_product_id:
        return []

    end = start + timedelta(days=days)
    pos = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.product_id == silo.odoo_product_id,
            PurchaseOrder.company_id == company_id,
            PurchaseOrder.state.in_(["draft", "purchase", "done"]),
            PurchaseOrder.date_planned.between(
                datetime(start.year, start.month, start.day, tzinfo=timezone.utc),
                datetime(end.year, end.month, end.day, tzinfo=timezone.utc),
            ),
        )
        .order_by(PurchaseOrder.date_planned.asc())
        .all()
    )

    return [
        {
            "date": po.date_planned.strftime("%Y-%m-%d"),
            "qty_kg": float(po.quantity),
            "po_name": po.name,
        }
        for po in pos
    ]


def _simulate(
    stock_kg: float,
    consumption_kg_day: float,
    po_events: list[dict],
    capacity_kg: float,
    start: date,
    days: int,
) -> list[dict]:
    """Simula la evolución del stock día a día.

    En cada día:
      1. Resta consumo
      2. Suma POs planificadas para ese día (capped a capacity)
      3. Floor a 0
    """
    # Indexar POs por fecha para O(1) lookup
    po_by_date: dict[str, float] = {}
    for ev in po_events:
        d = ev["date"]
        po_by_date[d] = po_by_date.get(d, 0.0) + ev["qty_kg"]

    points = []
    current = stock_kg

    for offset in range(days + 1):
        day = start + timedelta(days=offset)
        day_str = day.isoformat()

        if offset > 0:
            # Restar consumo del día
            current -= consumption_kg_day
            # Sumar POs que llegan este día
            if day_str in po_by_date:
                current += po_by_date[day_str]
            # Cap a capacidad máxima y floor a 0
            current = min(current, capacity_kg)
            current = max(current, 0.0)

        points.append({
            "date": day_str,
            "stock_kg": round(current, 1),
        })

    return points
