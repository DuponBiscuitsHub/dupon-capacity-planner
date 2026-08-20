"""0004 — Añadir campos vendor a purchase_orders

Revision ID: 0004_po_vendor_fields
Revises: 0003_kg_per_day
Create Date: 2026-08-20

Cambios:
  - purchase_orders: añade order_odoo_id, partner_name, vendor_confirmed
  - Estos campos ya existen en el ORM (odoo_replica.py) y sync_engine los
    escribe, pero faltaba la migración para PostgreSQL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_po_vendor_fields"
down_revision: Union[str, None] = "0003_kg_per_day"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str, schema: str) -> bool:
    """Check if a column already exists (idempotent migrations)."""
    from sqlalchemy import inspect as sa_inspect
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    columns = [c["name"] for c in inspector.get_columns(table_name, schema=schema)]
    return column_name in columns


def upgrade() -> None:
    schema = "odoo_replica"
    table = "purchase_orders"

    if not _has_column(table, "order_odoo_id", schema):
        op.add_column(
            table,
            sa.Column("order_odoo_id", sa.Integer(), nullable=True),
            schema=schema,
        )
        op.create_index(
            "ix_po_order_odoo_id",
            table,
            ["order_odoo_id"],
            schema=schema,
        )

    if not _has_column(table, "partner_name", schema):
        op.add_column(
            table,
            sa.Column("partner_name", sa.String(255), nullable=True),
            schema=schema,
        )

    if not _has_column(table, "vendor_confirmed", schema):
        op.add_column(
            table,
            sa.Column(
                "vendor_confirmed",
                sa.Boolean(),
                nullable=False,
                server_default="0",
            ),
            schema=schema,
        )


def downgrade() -> None:
    schema = "odoo_replica"
    table = "purchase_orders"

    if _has_column(table, "vendor_confirmed", schema):
        op.drop_column(table, "vendor_confirmed", schema=schema)

    if _has_column(table, "partner_name", schema):
        op.drop_column(table, "partner_name", schema=schema)

    if _has_column(table, "order_odoo_id", schema):
        op.drop_index("ix_po_order_odoo_id", table, schema=schema)
        op.drop_column(table, "order_odoo_id", schema=schema)
