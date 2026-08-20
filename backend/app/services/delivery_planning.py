"""
app/services/delivery_planning.py — Lógica de planificación de entregas.

Cruza las POs de Odoo (harina/azúcar/aceite) con las fechas sugeridas
por la app y calcula el semáforo (green/orange/red) para cada entrega.

Paradigma: Funcional — sin estado entre llamadas.
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.odoo_replica import PurchaseOrder
from app.models.planner import DeliverySuggestion, SiloConfig

_logger = logging.getLogger("app.delivery_planning")



# Tolerancia: si la PO llega antes de la fecha sugerida + este margen → verde
_ON_TIME_TOLERANCE_HOURS = 24


def get_delivery_plan(
    db: Session, company_id: int, days: int = 45,
) -> list[dict]:
    """Genera la tabla de planificación de entregas.

    Para cada PO de harina/azúcar/aceite (y para cada sugerencia sin PO),
    calcula el color del semáforo y la editabilidad.

    Returns:
        Lista de dicts con campos para la tabla frontend.
    """
    # Mapeo product_id → material_type desde silo_configs
    silos = db.query(SiloConfig).filter(
        SiloConfig.company_id == company_id,
    ).all()
    product_to_material: dict[int, str] = {}
    for s in silos:
        if s.odoo_product_id:
            product_to_material[s.odoo_product_id] = s.material_type

    if not product_to_material:
        return []

    silo_product_ids = list(product_to_material.keys())

    # Obtener POs de materiales de silo
    pos = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.product_id.in_(silo_product_ids),
            PurchaseOrder.company_id == company_id,
            PurchaseOrder.state.in_(["draft", "sent", "purchase", "done"]),
        )
        .order_by(PurchaseOrder.date_planned.asc())
        .all()
    )

    # Obtener sugerencias de la app
    suggestions = (
        db.query(DeliverySuggestion)
        .filter(
            DeliverySuggestion.company_id == company_id,
            DeliverySuggestion.status != "delivered",
        )
        .all()
    )

    # Indexar sugerencias por material_type para matching
    suggestion_by_material: dict[str, DeliverySuggestion] = {}
    for s in suggestions:
        if s.material_type not in suggestion_by_material:
            suggestion_by_material[s.material_type] = s

    result: list[dict] = []
    matched_materials: set[str] = set()

    for po in pos:
        material = product_to_material.get(po.product_id)
        if not material:
            continue

        suggestion = suggestion_by_material.get(material)
        app_date = suggestion.suggested_date if suggestion else None
        timing_color = _compute_timing_color(po, app_date)
        can_edit, edit_warning = _compute_editability(po)
        matched_materials.add(material)

        result.append(_build_row(
            material=material,
            po=po,
            app_suggested_date=app_date,
            timing_color=timing_color,
            can_edit=can_edit,
            edit_warning=edit_warning,
        ))

    # Sugerencias sin PO → fondo rojo, sin borde de confirmación
    for material, suggestion in suggestion_by_material.items():
        if material not in matched_materials:
            result.append({
                "material_type": material,
                "po_line_odoo_id": None,
                "order_odoo_id": None,
                "po_name": None,
                "partner_name": None,
                "product_ref": None,
                "vendor_confirmed": False,
                "timing_color": "red",
                "po_qty_kg": None,
                "po_date_planned": None,
                "po_state": None,
                "app_suggested_date": suggestion.suggested_date.isoformat(),
                "can_edit": False,
                "edit_warning": None,
            })

    return result


def _compute_timing_color(
    po: PurchaseOrder, app_date: datetime | None,
) -> str:
    """Calcula el color de fondo según el timing (independiente de vendor_confirmed).

    Verde:   PO existe y llega a tiempo según la app.
    Naranja: PO existe pero llega tarde según la app.
    Rojo:    Sin PO (nunca se llama en ese caso — ver sugerencias sin PO).
    """
    if not app_date or not po.date_planned:
        return "green"  # PO existe pero sin fecha de referencia → verde por defecto

    deadline = app_date + timedelta(hours=_ON_TIME_TOLERANCE_HOURS)
    if po.date_planned <= deadline:
        return "green"
    return "orange"


def _compute_editability(po: PurchaseOrder) -> tuple[bool, str | None]:
    """Determina si la fecha de la PO se puede editar.

    - done/cancel → bloqueado
    - vendor_confirmed=True → editable con warning (proveedor ya lo tiene)
    - resto → edición libre
    """
    if po.state in ("done", "cancel"):
        return False, "poEditBlocked"

    if po.vendor_confirmed:
        return True, "poEditWarningConfirmed"

    return True, None


def _build_row(
    material: str,
    po: PurchaseOrder,
    app_suggested_date: datetime | None,
    timing_color: str,
    can_edit: bool,
    edit_warning: str | None,
) -> dict:
    product_ref = None
    if po.product:
        ref = po.product.default_code or ""
        product_ref = f"[{ref}] {po.product.name}" if ref else po.product.name
    return {
        "material_type": material,
        "po_line_odoo_id": po.odoo_id,
        "order_odoo_id": po.order_odoo_id,
        "po_name": po.name,
        "partner_name": po.partner_name,
        "product_ref": product_ref,
        "vendor_confirmed": po.vendor_confirmed,
        "timing_color": timing_color,
        "po_qty_kg": float(po.quantity),
        "po_date_planned": po.date_planned.isoformat() if po.date_planned else None,
        "po_state": po.state,
        "app_suggested_date": app_suggested_date.isoformat() if app_suggested_date else None,
        "can_edit": can_edit,
        "edit_warning": edit_warning,
    }
