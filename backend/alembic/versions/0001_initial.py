"""initial schema — odoo_replica + dcp_app

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-06

Crea todos los schemas y tablas desde cero.
Ejecutar una sola vez antes del primer deploy en producción.

Para correr:
  cd backend
  env -i DATABASE_URL="postgresql://..." JWT_SECRET="..." ODOO_MODE=mock \\
    ../.venv/bin/alembic upgrade head
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Los schemas se crean en alembic/env.py antes de correr migraciones.
    # Aquí solo creamos las tablas.

    # ── odoo_replica.products ─────────────────────────────────────────────
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_code", sa.String(length=100), nullable=True),
        sa.Column("categ_id", sa.Integer(), nullable=True),
        sa.Column("uom_id", sa.Integer(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── odoo_replica.stock_quants ─────────────────────────────────────────
    op.create_table(
        "stock_quants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Numeric(precision=14, scale=3), nullable=False, server_default="0"),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── odoo_replica.mrp_boms ─────────────────────────────────────────────
    op.create_table(
        "mrp_boms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("product_tmpl_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_qty", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    op.create_table(
        "mrp_bom_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("bom_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_qty", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("product_uom_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── odoo_replica.mrp_workcenters ──────────────────────────────────────
    op.create_table(
        "mrp_workcenters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── odoo_replica.mrp_productions ─────────────────────────────────────
    op.create_table(
        "mrp_productions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_qty", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("workcenter_id", sa.Integer(), nullable=True),
        sa.Column("date_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_finished", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── odoo_replica.purchase_orders ──────────────────────────────────────
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("date_approve", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_planned", sa.DateTime(timezone=True), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_qty", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
        schema="odoo_replica",
    )

    # ── dcp_app.users ─────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        schema="dcp_app",
    )

    # ── dcp_app.silo_configs ──────────────────────────────────────────────
    op.create_table(
        "silo_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("silo_code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("material_type", sa.String(length=50), nullable=False),
        sa.Column("capacity_kg", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("safety_stock_kg", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("odoo_location_id", sa.Integer(), nullable=True),
        sa.Column("odoo_product_id", sa.Integer(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="dcp_app",
    )
    op.create_index("ix_silo_configs_company", "silo_configs", ["company_id"], schema="dcp_app")

    # ── dcp_app.line_capacities ───────────────────────────────────────────
    op.create_table(
        "line_capacities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("line_code", sa.String(length=10), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("consumption_kg_h", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("odoo_workcenter_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="dcp_app",
    )
    op.create_index("ix_line_cap_company", "line_capacities", ["company_id"], schema="dcp_app")

    # ── dcp_app.delivery_suggestions ─────────────────────────────────────
    op.create_table(
        "delivery_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("silo_id", sa.Integer(), nullable=False),
        sa.Column("silo_code", sa.String(length=20), nullable=False),
        sa.Column("material_type", sa.String(length=50), nullable=False),
        sa.Column("suggested_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("qty_kg", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("po_odoo_id", sa.Integer(), nullable=True),
        sa.Column("po_name", sa.String(length=100), nullable=True),
        sa.Column("po_state", sa.String(length=50), nullable=True),
        sa.Column("po_date_planned", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["silo_id"], ["dcp_app.silo_configs.id"]),
        schema="dcp_app",
    )
    op.create_index("ix_delivery_company", "delivery_suggestions", ["company_id", "status"], schema="dcp_app")

    # ── dcp_app.sync_logs ─────────────────────────────────────────────────
    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("records_synced", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="dcp_app",
    )

    # ── Seed inicial: silos Ibérica ───────────────────────────────────────
    # Los IDs de Odoo (location_id, product_id) quedan a NULL hasta resolver TBDs.
    op.execute("""
        INSERT INTO dcp_app.silo_configs
            (silo_code, name, material_type, capacity_kg, safety_stock_kg, company_id)
        VALUES
            ('S-H1', 'Silo Harina 1', 'harina', 25000, 2000, 1),
            ('S-H2', 'Silo Harina 2', 'harina', 25000, 2000, 1),
            ('S-H3', 'Silo Harina 3', 'harina', 25000, 2000, 1),
            ('S-AZ', 'Silo Azúcar',   'azucar', 30000, 2500, 1),
            ('S-AC', 'Silo Aceite',   'aceite_coco', 20000, 1500, 1)
        ON CONFLICT DO NOTHING;
    """)

    # Seed: líneas L01-L10 Ibérica (consumo a 0 hasta conocer capacidades reales)
    lines_sql = ", ".join(
        f"('L{i:02d}', 1, 0, false)" for i in range(1, 11)
    )
    op.execute(f"""
        INSERT INTO dcp_app.line_capacities (line_code, company_id, consumption_kg_h, is_active)
        VALUES {lines_sql}
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    # Elimina en orden inverso para respetar FK
    op.drop_table("sync_logs", schema="dcp_app")
    op.drop_table("delivery_suggestions", schema="dcp_app")
    op.drop_table("line_capacities", schema="dcp_app")
    op.drop_table("silo_configs", schema="dcp_app")
    op.drop_table("users", schema="dcp_app")
    op.drop_table("purchase_orders", schema="odoo_replica")
    op.drop_table("mrp_productions", schema="odoo_replica")
    op.drop_table("mrp_workcenters", schema="odoo_replica")
    op.drop_table("mrp_bom_lines", schema="odoo_replica")
    op.drop_table("mrp_boms", schema="odoo_replica")
    op.drop_table("stock_quants", schema="odoo_replica")
    op.drop_table("products", schema="odoo_replica")
