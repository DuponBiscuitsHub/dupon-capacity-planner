"""
app/models/planner.py — Tablas propias de la aplicación DCP.

Schema: dcp_app
Tablas: usuarios, configuración de silos, capacidad por línea,
        sugerencias de entrega, log de sincronización,
        tabla de referencia CON (consumos teóricos por formato),
        factores de corrección diarios (auto-calibrados).
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Date, Integer, String, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Company(Base):
    """Compañía (tenant) para soporte multicompany.

    Cada company_id en el sistema referencia esta tabla.
    Se mapea con res.company de Odoo.
    """
    __tablename__ = "companies"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    odoo_company_id = Column(Integer, nullable=True, unique=True)
    short_code = Column(String(8), nullable=True, unique=True)  # "IBE", "GUD"
    is_active = Column(Boolean, default=True, nullable=False)


class User(Base):
    """Usuarios de la app con RBAC de 2 niveles.

    Roles:
      'it'   — Admin total: gestión de usuarios, config, sync forzado.
      'user' — Operativo: ver silos, ver entregas, recalcular.
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(8), nullable=False)  # 'it' | 'user'
    is_active = Column(Boolean, default=True, nullable=False)
    # Compañía por defecto al hacer login
    default_company_id = Column(Integer, ForeignKey("dcp_app.companies.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    default_company = relationship("Company", foreign_keys=[default_company_id])



class SiloConfig(Base):
    """Configuración física de cada silo de primera materia.

    location_id: ID de Odoo que corresponde a la ubicación de este silo
    (TBD-3: pendiente confirmar con IT).
    """
    __tablename__ = "silo_configs"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    silo_code = Column(String(16), unique=True, nullable=False, index=True)  # S-H1, S-AZ, S-AC
    name = Column(String(128), nullable=False)
    material_type = Column(String(32), nullable=False)  # harina, azucar, aceite
    odoo_product_id = Column(Integer, nullable=True)   # TBD-4: product_id de Odoo
    odoo_location_id = Column(Integer, nullable=True)  # TBD-3: location_id del silo en Odoo
    capacity_kg = Column(Numeric(12, 2), nullable=False)
    safety_stock_kg = Column(Numeric(12, 2), nullable=False, default=0.0)
    company_id = Column(Integer, nullable=False, index=True)


class LineCapacity(Base):
    """Capacidad teórica de producción por línea de galleta.

    Configurable desde la UI por el planificador.
    Se usa para proyectar el consumo de primera materia.

    line_code: código de la línea (L01-L10). Debe coincidir con
    el Workcenter.code sincronizado desde Odoo (TBD-5).
    """
    __tablename__ = "line_capacities"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_code = Column(String(8), nullable=False, index=True)  # L01, L02, ...
    capacity_kg_h = Column(Numeric(10, 2), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)
    updated_by = Column(Integer, ForeignKey("dcp_app.users.id"), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    updater = relationship("User", foreign_keys=[updated_by])


class DeliverySuggestion(Base):
    """Sugerencia de descarga de camión para un silo.

    Estados:
      draft      (⚪) — Calculada, sin PO en Odoo.
      po_pending (🟡) — PO existe en Odoo pero no confirmada/sin fecha firme.
      confirmed  (✅) — PO confirmada + fecha de entrega acordada. NO se recalcula.
      delivered  (📦) — Recepción confirmada en Odoo.

    Regla: el motor de recálculo NUNCA toca registros con status='confirmed'.
    """
    __tablename__ = "delivery_suggestions"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    silo_code = Column(String(16), nullable=False, index=True)
    material_type = Column(String(32), nullable=False)
    suggested_date = Column(DateTime(timezone=True), nullable=False)
    qty_kg = Column(Numeric(12, 2), nullable=False)
    # PO linking (populated by recalculate when a PO exists in Odoo)
    po_odoo_id = Column(Integer, nullable=True)
    po_name = Column(String(64), nullable=True)   # Ej. "PO-00142"
    po_state = Column(String(32), nullable=True)  # draft, purchase, done, cancel
    status = Column(String(16), nullable=False, default="draft")
    company_id = Column(Integer, nullable=False, index=True)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SyncLog(Base):
    """Auditoría de ejecuciones del sync engine."""
    __tablename__ = "sync_log"
    __table_args__ = {"schema": "dcp_app"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(128), nullable=False)
    status = Column(String(16), nullable=False)     # success | failure
    records_synced = Column(Integer, nullable=False, default=0)
    error_message = Column(String, nullable=True)
    synced_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RefConsumptionRate(Base):
    """Consumos teóricos de referencia por formato (fuente: tabla CON del Excel).

    SSoT para consumos: kg/día por máquina (24h) por formato × material.
    Editable desde el panel IT → tab "Recetas".
    No se sincroniza con Odoo.

    Unidad: kg consumidos por 1 máquina en 24h de producción continua.
    Para rotativos (L01/L02/L06): 1 máquina = 1 horno rotativo.
    Para lineales (HAAS/Mini): 1 máquina = 1 línea completa.
    """
    __tablename__ = "ref_consumption_rates"
    __table_args__ = (
        UniqueConstraint("format_code", "material_type", "company_id", name="uq_ref_rate_v2"),
        {"schema": "dcp_app"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Código del formato+receta. Ej: "STD_R_110", "HAAS_110", "HAAS_98_OREO"
    format_code = Column(String(32), nullable=False, index=True)
    # "harina" | "azucar" | "aceite" | "lecitina" | "sal" | "carbonat" | "caramelina" | "maltitol" | "cacao" | "colorante" | "oli_bany"
    material_type = Column(String(32), nullable=False)
    # kg consumidos por 1 máquina en 24h
    kg_per_day = Column(Numeric(10, 2), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)
    updated_by = Column(Integer, ForeignKey("dcp_app.users.id"), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    updater = relationship("User", foreign_keys=[updated_by])


class LineFormat(Base):
    """Mapping: qué formatos puede ejecutar cada línea de producción.

    machines: número de máquinas por línea para este formato.
      - Rotativos (L01_L02, L06): 8 hornos por línea
      - Lineales (L03-L10): 1 máquina = 1 línea

    El cálculo de consumo usa: kg_per_day × machines × días_programados.
    """
    __tablename__ = "line_formats"
    __table_args__ = (
        UniqueConstraint("line_code", "format_code", "company_id", name="uq_line_format"),
        {"schema": "dcp_app"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_code = Column(String(8), nullable=False, index=True)    # L01_L02, L03, ..., L10
    format_code = Column(String(32), nullable=False, index=True) # STD_R_110, HAAS_110, ...
    machines = Column(Integer, nullable=False, default=1)         # 8 para rotativos, 1 para lineales
    company_id = Column(Integer, nullable=False, index=True)


class ProductFormatMapping(Base):
    """Mapping: producto Odoo → formato de producción.

    Permite saber qué formato (y por tanto qué consumos) aplican
    cuando una MO de Odoo referencia un producto concreto.
    Se pobla manualmente cuando se confirmen los product_ids reales.
    """
    __tablename__ = "product_format_mappings"
    __table_args__ = (
        UniqueConstraint("odoo_product_id", "company_id", name="uq_product_format"),
        {"schema": "dcp_app"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    odoo_product_id = Column(Integer, nullable=False, index=True)
    format_code = Column(String(32), nullable=False)
    company_id = Column(Integer, nullable=False, index=True)


class CorrectionFactor(Base):
    """Factor de corrección diario por material, auto-calibrado.

    Refleja la desviación entre el consumo teórico de Odoo y el consumo real
    observado (que incluye mermas de arranque, paros parciales, ajustes de
    sala de pasta ya registrados en Odoo).

    Cálculo (ejecutado por correction_engine.py tras cada sync):
      stock_expected = stock_ayer + entradas_hoy - consumo_teórico_hoy
      stock_actual   = stock.quant de Odoo (ya incluye ajuste sala de pasta)
      consumo_real   = stock_ayer + entradas_hoy - stock_actual
      factor         = consumo_real / consumo_teórico   (default 1.0 si = 0)

    factor > 1.0 → se consumió MÁS de lo esperado (merma arranque, etc.)
    factor < 1.0 → se consumió MENOS (paro parcial, receta más eficiente)
    """
    __tablename__ = "correction_factors"
    __table_args__ = (
        UniqueConstraint("date", "material_type", "company_id", name="uq_correction_day"),
        {"schema": "dcp_app"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    material_type = Column(String(32), nullable=False)   # "harina" | "azucar" | "aceite"
    company_id = Column(Integer, nullable=False, index=True)

    # Datos del cálculo para trazabilidad
    stock_expected_kg = Column(Numeric(12, 2), nullable=True)
    stock_actual_kg = Column(Numeric(12, 2), nullable=True)
    consumption_theoretical_kg = Column(Numeric(12, 2), nullable=True)
    consumption_actual_kg = Column(Numeric(12, 2), nullable=True)

    # Factor resultante: el motor de cálculo lo usa como multiplicador
    factor = Column(Numeric(6, 4), nullable=False, default=1.0)

    # "auto" = calculado por correction_engine | "seeded" = valor inicial del Excel
    source = Column(String(16), nullable=False, default="auto")

    calculated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

