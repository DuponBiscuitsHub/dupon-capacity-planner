"""
app/core/sync_engine.py — Orquestador de sincronización Odoo → PostgreSQL.

Sincroniza los datos mínimos de Odoo necesarios para calcular entregas:
  - products (primera materia + productos galleta)
  - workcenters (líneas de galleta)
  - stock_quants (niveles de silos)
  - mrp_productions (MOs activas/planificadas)
  - mrp_boms + mrp_bom_lines (consumo por receta)
  - purchase_orders (POs de primera materia)

Paradigma: OOP — tiene estado (db session, client).
Nota: los métodos son síncronos para compatibilidad con run_in_executor.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.odoo_client import OdooClient
from app.models.odoo_replica import (
    MrpBom,
    MrpBomLine,
    MrpProduction,
    Product,
    PurchaseOrder,
    StockQuant,
    Workcenter,
)
from app.models.planner import SiloConfig, SyncLog

_logger = logging.getLogger("app.sync_engine")


class OdooSyncEngine:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.client = OdooClient(
            base_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            user=settings.ODOO_USER,
            api_key=settings.ODOO_API_KEY,
        )

    def run_full_sync(self) -> None:
        """Ejecuta el pipeline completo de sync en orden de dependencias."""
        if settings.ODOO_MODE == "mock":
            _logger.info("ODOO_MODE=mock — skipping real sync.")
            return

        _logger.info("Starting full Odoo sync.")
        self.sync_products()
        self.sync_workcenters()
        self.sync_stock_quants()
        self.sync_manufacturing_orders()
        self.sync_boms()
        self.sync_purchase_orders()
        _logger.info("Full Odoo sync complete.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _log(self, model_name: str, status: str, count: int = 0, error: str | None = None) -> None:
        self.db.add(SyncLog(
            model_name=model_name,
            status=status,
            records_synced=count,
            error_message=error,
            synced_at=datetime.now(timezone.utc),
        ))
        self.db.commit()

    def _search_read(self, model: str, domain: list, fields: list, limit: int = 0) -> list:
        """Wrapper para search_read del OdooClient síncrono."""
        return self.client.search_read(model=model, domain=domain, fields=fields, limit=limit)

    @staticmethod
    def _many2one_id(value) -> int | None:
        """Extrae el ID de un campo Many2one de Odoo ([id, name] o False)."""
        if isinstance(value, list) and value:
            return int(value[0])
        return None

    # ── Sync methods ──────────────────────────────────────────────────────────

    def sync_products(self) -> int:
        """Sincroniza productos de primera materia y galleta."""
        try:
            records = self._search_read(
                model="product.product",
                domain=[["active", "=", True]],
                fields=["id", "name", "default_code", "uom_id", "company_id"],
            )
            count = 0
            for r in records:
                company_id = self._many2one_id(r.get("company_id")) or 1
                existing = self.db.query(Product).filter_by(odoo_id=r["id"]).first()
                if existing:
                    existing.name = r["name"]
                    existing.default_code = r.get("default_code") or None
                    existing.company_id = company_id
                else:
                    self.db.add(Product(
                        odoo_id=r["id"],
                        name=r["name"],
                        default_code=r.get("default_code") or None,
                        company_id=company_id,
                    ))
                count += 1
            self.db.commit()
            self._log("product.product", "success", count)
            _logger.info("Products synced: %d", count)
            return count
        except Exception as exc:
            self._log("product.product", "failure", error=str(exc))
            _logger.error("sync_products failed: %s", exc)
            raise

    def sync_workcenters(self) -> int:
        """Sincroniza centros de trabajo (líneas de galleta)."""
        try:
            records = self._search_read(
                model="mrp.workcenter",
                domain=[["active", "=", True]],
                fields=["id", "name", "code", "company_id"],
            )
            count = 0
            for r in records:
                company_id = self._many2one_id(r.get("company_id")) or 1
                existing = self.db.query(Workcenter).filter_by(odoo_id=r["id"]).first()
                if existing:
                    existing.name = r["name"]
                    existing.code = r.get("code") or None
                    existing.company_id = company_id
                else:
                    self.db.add(Workcenter(
                        odoo_id=r["id"],
                        name=r["name"],
                        code=r.get("code") or None,
                        company_id=company_id,
                    ))
                count += 1
            self.db.commit()
            self._log("mrp.workcenter", "success", count)
            return count
        except Exception as exc:
            self._log("mrp.workcenter", "failure", error=str(exc))
            raise

    def sync_stock_quants(self) -> int:
        """Sincroniza niveles de inventario de silos.

        Filtra por los odoo_location_id configurados en SiloConfig para evitar
        traer stock de ubicaciones no relevantes (A2/Stock, etc.).
        Si ningún silo tiene odoo_location_id configurado, hace fallback a todas
        las ubicaciones internas (modo degradado).
        """
        try:
            # Lee los location_ids de silo configurados en la BD
            silo_location_ids = [
                s.odoo_location_id
                for s in self.db.query(SiloConfig).filter(
                    SiloConfig.odoo_location_id.isnot(None)
                ).all()
            ]

            if silo_location_ids:
                domain = [["location_id", "in", silo_location_ids]]
                _logger.info("Syncing quants for silo locations: %s", silo_location_ids)
            else:
                # Fallback: todas las internas (staging sin configurar)
                domain = [["location_id.usage", "=", "internal"]]
                _logger.warning("No silo odoo_location_ids configured — fallback to all internal locs")

            records = self._search_read(
                model="stock.quant",
                domain=domain,
                fields=["id", "product_id", "location_id", "quantity", "reserved_quantity", "company_id"],
            )
            count = 0
            for r in records:
                product_id = self._many2one_id(r.get("product_id"))
                location_id = self._many2one_id(r.get("location_id"))
                company_id = self._many2one_id(r.get("company_id")) or 1
                if not product_id or not location_id:
                    continue

                existing = self.db.query(StockQuant).filter_by(odoo_id=r["id"]).first()
                if existing:
                    existing.quantity = float(r.get("quantity") or 0.0)
                    existing.reserved_quantity = float(r.get("reserved_quantity") or 0.0)
                else:
                    self.db.add(StockQuant(
                        odoo_id=r["id"],
                        product_id=product_id,
                        location_id=location_id,
                        quantity=float(r.get("quantity") or 0.0),
                        reserved_quantity=float(r.get("reserved_quantity") or 0.0),
                        company_id=company_id,
                    ))
                count += 1
            self.db.commit()
            self._log("stock.quant", "success", count)
            _logger.info("Stock quants synced: %d (locations=%s)", count, silo_location_ids)
            return count
        except Exception as exc:
            self._log("stock.quant", "failure", error=str(exc))
            raise

    def sync_manufacturing_orders(self) -> int:
        """Sincroniza MOs activas/planificadas de galleta."""
        try:
            records = self._search_read(
                model="mrp.production",
                domain=[["state", "in", ["draft", "confirmed", "progress"]]],
                fields=["id", "name", "product_id", "workcenter_id", "product_qty",
                        "state", "date_start", "date_deadline", "company_id"],
            )
            count = 0
            for r in records:
                product_id = self._many2one_id(r.get("product_id"))
                workcenter_id = self._many2one_id(r.get("workcenter_id"))
                company_id = self._many2one_id(r.get("company_id")) or 1
                if not product_id:
                    continue

                date_start = _parse_dt(r.get("date_start"))
                date_finished = _parse_dt(r.get("date_deadline"))

                existing = self.db.query(MrpProduction).filter_by(odoo_id=r["id"]).first()
                if existing:
                    existing.state = r["state"]
                    existing.date_planned_start = date_start
                    existing.date_planned_finished = date_finished
                    existing.workcenter_id = workcenter_id
                else:
                    self.db.add(MrpProduction(
                        odoo_id=r["id"],
                        name=r["name"],
                        product_id=product_id,
                        workcenter_id=workcenter_id,
                        qty_to_produce=float(r.get("product_qty") or 0.0),
                        state=r["state"],
                        date_planned_start=date_start,
                        date_planned_finished=date_finished,
                        company_id=company_id,
                    ))
                count += 1
            self.db.commit()
            self._log("mrp.production", "success", count)
            return count
        except Exception as exc:
            self._log("mrp.production", "failure", error=str(exc))
            raise

    def sync_boms(self) -> int:
        """Sincroniza BOMs y sus líneas (consumo por receta)."""
        try:
            boms = self._search_read(
                model="mrp.bom",
                domain=[["active", "=", True]],
                fields=["id", "product_id", "code", "product_qty", "company_id"],
            )
            count = 0
            for b in boms:
                product_id = self._many2one_id(b.get("product_id"))
                company_id = self._many2one_id(b.get("company_id")) or 1
                if not product_id:
                    continue

                existing = self.db.query(MrpBom).filter_by(odoo_id=b["id"]).first()
                if existing:
                    existing.product_id = product_id
                    existing.quantity = float(b.get("product_qty") or 1.0)
                else:
                    self.db.add(MrpBom(
                        odoo_id=b["id"],
                        product_id=product_id,
                        code=b.get("code") or None,
                        quantity=float(b.get("product_qty") or 1.0),
                        company_id=company_id,
                    ))
                count += 1

            # Sincronizar líneas de BOM
            bom_lines = self._search_read(
                model="mrp.bom.line",
                domain=[],
                fields=["id", "bom_id", "product_id", "product_qty"],
            )
            for bl in bom_lines:
                bom_id = self._many2one_id(bl.get("bom_id"))
                product_id = self._many2one_id(bl.get("product_id"))
                if not bom_id or not product_id:
                    continue
                existing = self.db.query(MrpBomLine).filter_by(odoo_id=bl["id"]).first()
                if existing:
                    existing.product_qty = float(bl.get("product_qty") or 0.0)
                else:
                    self.db.add(MrpBomLine(
                        odoo_id=bl["id"],
                        bom_id=bom_id,
                        product_id=product_id,
                        product_qty=float(bl.get("product_qty") or 0.0),
                    ))

            self.db.commit()
            self._log("mrp.bom", "success", count)
            return count
        except Exception as exc:
            self._log("mrp.bom", "failure", error=str(exc))
            raise

    def sync_purchase_orders(self) -> int:
        """Sincroniza líneas de PO de primera materia abiertas.

        Odoo JSON-RPC no soporta dot-notation (order_id.state) en campos.
        Se leen los estados de purchase.order por separado y se cruzan.
        """
        try:
            # 1. Leer POs abiertas (con su estado)
            orders = self._search_read(
                model="purchase.order",
                domain=[["state", "in", ["draft", "sent", "purchase", "done"]]],
                fields=["id", "name", "state", "company_id", "partner_id", "vendor_confirmed"],
            )
            order_map: dict[int, dict] = {o["id"]: o for o in orders}
            order_ids = list(order_map.keys())

            if not order_ids:
                self._log("purchase.order.line", "success", 0)
                return 0

            # 2. Leer líneas de esas POs
            records = self._search_read(
                model="purchase.order.line",
                domain=[["order_id", "in", order_ids]],
                fields=["id", "order_id", "product_id", "product_qty",
                        "date_planned", "company_id"],
            )
            count = 0
            for r in records:
                product_id = self._many2one_id(r.get("product_id"))
                company_id = self._many2one_id(r.get("company_id")) or 1
                order_ref   = r.get("order_id")
                order_id_val = self._many2one_id(order_ref) if isinstance(order_ref, list) else None
                po_name = order_ref[1] if isinstance(order_ref, list) else str(order_ref)
                po_state        = order_map.get(order_id_val, {}).get("state", "draft") if order_id_val else "draft"
                partner_raw     = order_map.get(order_id_val, {}).get("partner_id") if order_id_val else None
                partner_name    = partner_raw[1] if isinstance(partner_raw, list) and len(partner_raw) > 1 else None
                vendor_confirmed = bool(order_map.get(order_id_val, {}).get("vendor_confirmed", False)) if order_id_val else False

                if not product_id:
                    continue

                existing = self.db.query(PurchaseOrder).filter_by(odoo_id=r["id"]).first()
                if existing:
                    existing.order_odoo_id   = order_id_val
                    existing.state           = po_state
                    existing.date_planned    = _parse_dt(r.get("date_planned"))
                    existing.quantity        = float(r.get("product_qty") or 0.0)
                    existing.partner_name    = partner_name
                    existing.vendor_confirmed = vendor_confirmed
                else:
                    self.db.add(PurchaseOrder(
                        odoo_id=r["id"],
                        order_odoo_id=order_id_val,
                        name=po_name,
                        partner_name=partner_name,
                        vendor_confirmed=vendor_confirmed,
                        product_id=product_id,
                        quantity=float(r.get("product_qty") or 0.0),
                        date_planned=_parse_dt(r.get("date_planned")),
                        state=po_state,
                        company_id=company_id,
                    ))
                count += 1
            self.db.commit()
            self._log("purchase.order.line", "success", count)
            _logger.info("Purchase order lines synced: %d", count)
            return count
        except Exception as exc:
            self._log("purchase.order.line", "failure", error=str(exc))
            _logger.error("sync_purchase_orders failed: %s", exc)
            raise


def _parse_dt(value: str | None) -> datetime | None:
    """Parsea un string de fecha/hora de Odoo (ISO 8601) a datetime UTC."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
