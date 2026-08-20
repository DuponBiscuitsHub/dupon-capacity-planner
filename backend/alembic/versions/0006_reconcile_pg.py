"""0006 — Reconciliación: alinear BD PostgreSQL legacy con ORM actual

Revision ID: 0006_reconcile_pg
Revises: 0005_companies_multicompany
Create Date: 2026-08-20

Contexto:
  La BD PostgreSQL fue creada con un migration chain antiguo (rev b21025bdaf67)
  antes de la simplificación a Raw Material Planner. Las tablas base existen
  pero con un schema diferente. Esta migración:

  1. Crea tablas que faltan (companies, line_capacities, delivery_suggestions,
     correction_factors, ref_consumption_rates, line_formats, product_format_mappings)
  2. Añade columnas que faltan en tablas existentes (users, purchase_orders, silo_configs)
  3. Seed de companies y silo_configs para Ibérica
  4. NO toca tablas legacy (simulation_scenarios, etc.) — se dejan como están

  Todas las operaciones son idempotentes (_has_table / _has_column checks).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_reconcile_pg"
down_revision: Union[str, None] = "0005_companies_multicompany"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str, schema: str) -> bool:
    from sqlalchemy import inspect as sa_inspect
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    return table_name in inspector.get_table_names(schema=schema)


def _has_column(table_name: str, column_name: str, schema: str) -> bool:
    from sqlalchemy import inspect as sa_inspect
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    columns = [c["name"] for c in inspector.get_columns(table_name, schema=schema)]
    return column_name in columns


def upgrade() -> None:
    app = "dcp_app"
    replica = "odoo_replica"

    # ══════════════════════════════════════════════════════════════════════
    # 1. TABLAS NUEVAS en dcp_app
    # ══════════════════════════════════════════════════════════════════════

    # ── companies ─────────────────────────────────────────────────────────
    if not _has_table("companies", app):
        op.create_table(
            "companies",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("odoo_company_id", sa.Integer(), nullable=True),
            sa.Column("short_code", sa.String(8), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("odoo_company_id"),
            sa.UniqueConstraint("short_code"),
            schema=app,
        )
        # Seed
        companies_t = sa.table(
            "companies",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
            sa.column("odoo_company_id", sa.Integer),
            sa.column("short_code", sa.String),
            sa.column("is_active", sa.Boolean),
            schema=app,
        )
        op.bulk_insert(companies_t, [
            {"id": 1, "name": "Dupon Biscuits Ibérica SAU", "odoo_company_id": 1, "short_code": "IBE", "is_active": True},
            {"id": 2, "name": "Dupon Biscuits Gudensberg", "odoo_company_id": 2, "short_code": "GUD", "is_active": True},
            {"id": 3, "name": "Dupon Biscuits France", "odoo_company_id": 3, "short_code": "FRA", "is_active": True},
            {"id": 4, "name": "Dupon Biscuits Italia", "odoo_company_id": 4, "short_code": "ITA", "is_active": True},
            {"id": 5, "name": "Dupon Biscuits Belgium", "odoo_company_id": 5, "short_code": "BEL", "is_active": True},
        ])

    # ── line_capacities ───────────────────────────────────────────────────
    if not _has_table("line_capacities", app):
        op.create_table(
            "line_capacities",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("line_code", sa.String(8), nullable=False, index=True),
            sa.Column("capacity_kg_h", sa.Numeric(10, 2), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.Column("updated_by", sa.Integer(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["updated_by"], [f"{app}.users.id"]),
            schema=app,
        )

    # ── delivery_suggestions ──────────────────────────────────────────────
    if not _has_table("delivery_suggestions", app):
        op.create_table(
            "delivery_suggestions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("silo_code", sa.String(16), nullable=False, index=True),
            sa.Column("material_type", sa.String(32), nullable=False),
            sa.Column("suggested_date", sa.DateTime(timezone=True), nullable=False),
            sa.Column("qty_kg", sa.Numeric(12, 2), nullable=False),
            sa.Column("po_odoo_id", sa.Integer(), nullable=True),
            sa.Column("po_name", sa.String(64), nullable=True),
            sa.Column("po_state", sa.String(32), nullable=True),
            sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            schema=app,
        )

    # ── correction_factors ────────────────────────────────────────────────
    if not _has_table("correction_factors", app):
        op.create_table(
            "correction_factors",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("date", sa.Date(), nullable=False, index=True),
            sa.Column("material_type", sa.String(32), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.Column("stock_expected_kg", sa.Numeric(12, 2), nullable=True),
            sa.Column("stock_actual_kg", sa.Numeric(12, 2), nullable=True),
            sa.Column("consumption_theoretical_kg", sa.Numeric(12, 2), nullable=True),
            sa.Column("consumption_actual_kg", sa.Numeric(12, 2), nullable=True),
            sa.Column("factor", sa.Numeric(6, 4), nullable=False, server_default="1.0"),
            sa.Column("source", sa.String(16), nullable=False, server_default="auto"),
            sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("date", "material_type", "company_id", name="uq_correction_day"),
            schema=app,
        )

    # ── ref_consumption_rates ─────────────────────────────────────────────
    if not _has_table("ref_consumption_rates", app):
        op.create_table(
            "ref_consumption_rates",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("format_code", sa.String(32), nullable=False, index=True),
            sa.Column("material_type", sa.String(32), nullable=False),
            sa.Column("kg_per_day", sa.Numeric(10, 2), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.Column("updated_by", sa.Integer(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("format_code", "material_type", "company_id", name="uq_ref_rate_v2"),
            sa.ForeignKeyConstraint(["updated_by"], [f"{app}.users.id"]),
            schema=app,
        )

    # ── line_formats ──────────────────────────────────────────────────────
    if not _has_table("line_formats", app):
        op.create_table(
            "line_formats",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("line_code", sa.String(8), nullable=False, index=True),
            sa.Column("format_code", sa.String(32), nullable=False, index=True),
            sa.Column("machines", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("line_code", "format_code", "company_id", name="uq_line_format"),
            schema=app,
        )

    # ── product_format_mappings ───────────────────────────────────────────
    if not _has_table("product_format_mappings", app):
        op.create_table(
            "product_format_mappings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("odoo_product_id", sa.Integer(), nullable=False, index=True),
            sa.Column("format_code", sa.String(32), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False, index=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("odoo_product_id", "company_id", name="uq_product_format"),
            schema=app,
        )

    # ── sync_log (renombrar de sync_logs si existe con nombre legacy) ─────
    if not _has_table("sync_log", app) and _has_table("sync_logs", app):
        op.rename_table("sync_logs", "sync_log", schema=app)
    elif not _has_table("sync_log", app):
        op.create_table(
            "sync_log",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("model_name", sa.String(128), nullable=False),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("records_synced", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error_message", sa.String(), nullable=True),
            sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            schema=app,
        )

    # ══════════════════════════════════════════════════════════════════════
    # 2. COLUMNAS NUEVAS en tablas existentes
    # ══════════════════════════════════════════════════════════════════════

    # ── users.default_company_id ──────────────────────────────────────────
    if not _has_column("users", "default_company_id", app):
        op.add_column(
            "users",
            sa.Column("default_company_id", sa.Integer(), nullable=True),
            schema=app,
        )
        op.execute(f"UPDATE {app}.users SET default_company_id = 1")
        op.create_foreign_key(
            "fk_users_default_company", "users", "companies",
            ["default_company_id"], ["id"],
            source_schema=app, referent_schema=app,
        )

    # ── silo_configs: columnas que podrían faltar ─────────────────────────
    if not _has_column("silo_configs", "odoo_product_id", app):
        op.add_column(
            "silo_configs",
            sa.Column("odoo_product_id", sa.Integer(), nullable=True),
            schema=app,
        )

    if not _has_column("silo_configs", "company_id", app):
        op.add_column(
            "silo_configs",
            sa.Column("company_id", sa.Integer(), nullable=False, server_default="1"),
            schema=app,
        )

    # ── purchase_orders: campos v1.9+ ─────────────────────────────────────
    if not _has_column("purchase_orders", "order_odoo_id", replica):
        op.add_column(
            "purchase_orders",
            sa.Column("order_odoo_id", sa.Integer(), nullable=True),
            schema=replica,
        )
        op.create_index("ix_po_order_odoo_id", "purchase_orders", ["order_odoo_id"], schema=replica)

    if not _has_column("purchase_orders", "partner_name", replica):
        op.add_column(
            "purchase_orders",
            sa.Column("partner_name", sa.String(255), nullable=True),
            schema=replica,
        )

    if not _has_column("purchase_orders", "vendor_confirmed", replica):
        op.add_column(
            "purchase_orders",
            sa.Column("vendor_confirmed", sa.Boolean(), nullable=False, server_default="false"),
            schema=replica,
        )


def downgrade() -> None:
    # No implementado — esta migración de reconciliación no se revierte
    pass
