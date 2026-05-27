from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class User(Base):
    """
    ORM mapping for application users with Role-Based Access Control (RBAC).
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "dcp_app"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False)  # admin, planner, commercial, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SiloConfig(Base):
    """
    ORM mapping for custom physical silo settings.
    Links Odoo raw materials to storage capacities and safety stocks.
    """
    __tablename__ = "silo_configs"
    __table_args__ = {"schema": "dcp_app"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    silo_number = Column(Integer, nullable=False)
    silo_name = Column(String(128), nullable=False)
    product_id = Column(Integer, ForeignKey("odoo_replica.products.odoo_id"), nullable=False)
    capacity_kg = Column(Numeric(12, 2), nullable=False)
    safety_stock_kg = Column(Numeric(12, 2), nullable=False)
    critical_stock_kg = Column(Numeric(12, 2), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)

class SimulationScenario(Base):
    """
    ORM mapping for sandbox What-If simulation parameters (stored as JSONB).
    """
    __tablename__ = "simulation_scenarios"
    __table_args__ = {"schema": "dcp_app"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parameters = Column(JSONB, nullable=False)  # Config sliders state JSON
    created_by = Column(Integer, ForeignKey("dcp_app.users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("User", foreign_keys=[created_by])

class SyncLog(Base):
    """
    ORM mapping to audit the status, times and counts of Odoo sync tasks.
    """
    __tablename__ = "sync_logs"
    __table_args__ = {"schema": "dcp_app"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(128), nullable=False)
    last_sync_timestamp = Column(DateTime, nullable=False)
    status = Column(String(32), nullable=False)  # success, failure
    records_synced = Column(Integer, nullable=False, default=0)
    error_message = Column(String, nullable=True)
