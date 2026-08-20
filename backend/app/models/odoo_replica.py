"""
app/models/odoo_replica.py — Cache mínimo de Odoo (read-only).

Schema: odoo_replica
Tablas: productos primera materia, stock de silos, BOM galleta,
        MOs planificadas, centros de trabajo, purchase orders.

Regla: Solo primera materia galleta. Sin aluminio, ventas, ni trazabilidad.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "odoo_replica"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    default_code = Column(String(64), nullable=True)
    name = Column(String(255), nullable=False)
    uom_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=False, index=True)
    # CS-DATETIME-001: timezone=True persiste timestamptz en PostgreSQL
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class StockQuant(Base):
    """Niveles de inventario por ubicación (location_id).

    Para los silos se filtra por location_id configurado en silo_configs.
    """
    __tablename__ = "stock_quants"
    __table_args__ = {"schema": "odoo_replica"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    location_id = Column(Integer, nullable=False)
    quantity = Column(Numeric(12, 4), nullable=False, default=0.0)
    reserved_quantity = Column(Numeric(12, 4), nullable=False, default=0.0)
    company_id = Column(Integer, nullable=False, index=True)

    product = relationship("Product", foreign_keys=[product_id])


class MrpBom(Base):
    """Cabeceras de listas de materiales (mrp.bom en Odoo)."""
    __tablename__ = "mrp_boms"
    __table_args__ = {"schema": "odoo_replica"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    code = Column(String(64), nullable=True)
    quantity = Column(Numeric(12, 4), nullable=False, default=1.0)
    company_id = Column(Integer, nullable=False, index=True)

    product = relationship("Product", foreign_keys=[product_id])
    lines = relationship("MrpBomLine", back_populates="bom")


class MrpBomLine(Base):
    """Líneas de lista de materiales (mrp.bom.line en Odoo).

    product_qty es la cantidad de componente (ej. kg de harina) por unidad de BOM.
    """
    __tablename__ = "mrp_bom_lines"
    __table_args__ = {"schema": "odoo_replica"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    bom_id = Column(Integer, ForeignKey("odoo_replica.mrp_boms.odoo_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    product_qty = Column(Numeric(12, 4), nullable=False)

    bom = relationship("MrpBom", back_populates="lines")
    product = relationship("Product", foreign_keys=[product_id])


class Workcenter(Base):
    """Centros de trabajo = líneas de galleta (mrp.workcenter en Odoo)."""
    __tablename__ = "workcenters"
    __table_args__ = {"schema": "odoo_replica"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64), nullable=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)


class MrpProduction(Base):
    """Órdenes de fabricación (mrp.production en Odoo).

    Solo se sincronizan MOs de galleta (filtradas por workcenter de líneas galleta).
    Estados relevantes: draft, confirmed, progress, done.
    """
    __tablename__ = "mrp_productions"
    __table_args__ = (
        Index("idx_mo_company_state", "company_id", "state"),
        {"schema": "odoo_replica"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    workcenter_id = Column(Integer, ForeignKey("odoo_replica.workcenters.odoo_id"), nullable=True)
    qty_to_produce = Column(Numeric(12, 4), nullable=False)
    state = Column(String(32), nullable=False)  # draft, confirmed, progress, done
    date_planned_start = Column(DateTime, nullable=True)
    date_planned_finished = Column(DateTime, nullable=True)
    company_id = Column(Integer, nullable=False, index=True)

    product = relationship("Product", foreign_keys=[product_id])
    workcenter = relationship("Workcenter", foreign_keys=[workcenter_id])


class PurchaseOrder(Base):
    """Purchase Orders de primera materia (purchase.order.line en Odoo).

    Se usa para determinar si una sugerencia de entrega ya tiene PO
    y si la fecha está confirmada por el proveedor.
    """
    __tablename__ = "purchase_orders"
    __table_args__ = (
        Index("idx_po_product_state", "product_id", "state", "company_id"),
        {"schema": "odoo_replica"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    order_odoo_id = Column(Integer, nullable=True, index=True)  # ID de purchase.order (padre)
    name = Column(String(128), nullable=False)  # PO-XXXXX
    partner_name = Column(String(255), nullable=True)  # Nombre del proveedor
    vendor_confirmed = Column(Boolean, nullable=False, server_default="0")  # Confirmado por proveedor
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    quantity = Column(Numeric(12, 4), nullable=False)
    date_planned = Column(DateTime, nullable=True)  # Fecha acordada de entrega
    state = Column(String(32), nullable=False)  # draft, purchase (confirmed), done, cancel
    company_id = Column(Integer, nullable=False, index=True)

    product = relationship("Product", foreign_keys=[product_id])
