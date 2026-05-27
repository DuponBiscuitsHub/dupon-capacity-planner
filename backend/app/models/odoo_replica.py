from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import Base

class Product(Base):
    """
    ORM mapping for the replicated products (product.product in Odoo).
    """
    __tablename__ = "products"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    default_code = Column(String(64), nullable=True)
    name = Column(String(255), nullable=False)
    uom_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=False, index=True)
    # CS-DATETIME-001: timezone=True persiste el offset UTC en PostgreSQL (timestamptz).
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class StockQuant(Base):
    """
    ORM mapping for inventory levels (stock.quant in Odoo).
    Tracks real and reserved quantities per physical location.
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
    """
    ORM mapping for Bill of Materials headers (mrp.bom in Odoo).
    """
    __tablename__ = "mrp_boms"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    code = Column(String(64), nullable=True)
    quantity = Column(Numeric(12, 4), nullable=False, default=1.0)
    company_id = Column(Integer, nullable=False, index=True)
    
    product = relationship("Product", foreign_keys=[product_id])

class MrpBomLine(Base):
    """
    ORM mapping for Bill of Materials components details (mrp.bom.line in Odoo).
    """
    __tablename__ = "mrp_bom_lines"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    bom_id = Column(Integer, ForeignKey("odoo_replica.mrp_boms.odoo_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    product_qty = Column(Numeric(12, 4), nullable=False)
    scrap_factor = Column(Numeric(5, 2), nullable=False, default=0.0)
    
    bom = relationship("MrpBom", foreign_keys=[bom_id])
    product = relationship("Product", foreign_keys=[product_id])

class Workcenter(Base):
    """
    ORM mapping for physical Work Centers (mrp.workcenter in Odoo).
    """
    __tablename__ = "workcenters"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64), nullable=True)
    capacity_nominal = Column(Numeric(12, 2), nullable=False, default=1.0)
    efficiency = Column(Numeric(5, 2), nullable=False, default=100.0)
    company_id = Column(Integer, nullable=False, index=True)

class MrpProduction(Base):
    """
    ORM mapping for Manufacturing Orders (mrp.production in Odoo).
    """
    __tablename__ = "mrp_productions"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    qty_to_produce = Column(Numeric(12, 4), nullable=False)
    state = Column(String(32), nullable=False)
    date_planned_start = Column(DateTime, nullable=True)
    date_planned_finished = Column(DateTime, nullable=True)
    company_id = Column(Integer, nullable=False, index=True)
    
    product = relationship("Product", foreign_keys=[product_id])

class SaleOrder(Base):
    """
    ORM mapping for Sales Orders details (sale.order/sale.order.line in Odoo).
    Optimized for analytical queries.
    """
    __tablename__ = "sale_orders"
    __table_args__ = (
        Index("idx_so_analytics", "product_id", "date_delivery", "company_id"),
        {"schema": "odoo_replica"}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    quantity = Column(Numeric(12, 4), nullable=False)
    date_delivery = Column(DateTime, nullable=False)
    state = Column(String(32), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)
    
    product = relationship("Product", foreign_keys=[product_id])

class PurchaseOrder(Base):
    """
    ORM mapping for Purchase Orders and Inbound Shipments (purchase.order/purchase.order.line in Odoo).
    """
    __tablename__ = "purchase_orders"
    __table_args__ = {"schema": "odoo_replica"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    quantity = Column(Numeric(12, 4), nullable=False)
    date_planned = Column(DateTime, nullable=False)
    state = Column(String(32), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)
    
    product = relationship("Product", foreign_keys=[product_id])
