"""0005 — Crear tabla companies + añadir default_company_id a users

Revision ID: 0005_companies_multicompany
Revises: 0004_po_vendor_fields
Create Date: 2026-08-20

Cambios:
  - Crear dcp_app.companies (Company model)
  - Añadir users.default_company_id (FK a companies)
  - Seed: 5 compañías del grupo Dupon (IBE, GUD, FRA, ITA, BEL)
  - Asignar default_company_id=1 (IBE) a usuarios existentes

Contexto:
  La tabla companies y la columna default_company_id existían en el ORM
  y funcionaban en SQLite (via create_all), pero nunca tuvieron migración
  Alembic para PostgreSQL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_companies_multicompany"
down_revision: Union[str, None] = "0004_po_vendor_fields"
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
    schema = "dcp_app"

    # 1. Crear tabla companies
    if not _has_table("companies", schema):
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
            schema=schema,
        )

    # 2. Seed companies
    companies_table = sa.table(
        "companies",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("odoo_company_id", sa.Integer),
        sa.column("short_code", sa.String),
        sa.column("is_active", sa.Boolean),
        schema=schema,
    )
    op.bulk_insert(companies_table, [
        {"id": 1, "name": "Dupon Biscuits Ibérica SAU", "odoo_company_id": 1, "short_code": "IBE", "is_active": True},
        {"id": 2, "name": "Dupon Biscuits Gudensberg", "odoo_company_id": 2, "short_code": "GUD", "is_active": True},
        {"id": 3, "name": "Dupon Biscuits France", "odoo_company_id": 3, "short_code": "FRA", "is_active": True},
        {"id": 4, "name": "Dupon Biscuits Italia", "odoo_company_id": 4, "short_code": "ITA", "is_active": True},
        {"id": 5, "name": "Dupon Biscuits Belgium", "odoo_company_id": 5, "short_code": "BEL", "is_active": True},
    ])

    # 3. Añadir default_company_id a users
    if not _has_column("users", "default_company_id", schema):
        op.add_column(
            "users",
            sa.Column("default_company_id", sa.Integer(), nullable=True),
            schema=schema,
        )
        # Asignar IBE (id=1) a usuarios existentes
        op.execute(f"UPDATE {schema}.users SET default_company_id = 1")
        # Crear FK
        op.create_foreign_key(
            "fk_users_default_company",
            "users",
            "companies",
            ["default_company_id"],
            ["id"],
            source_schema=schema,
            referent_schema=schema,
        )


def downgrade() -> None:
    schema = "dcp_app"

    if _has_column("users", "default_company_id", schema):
        op.drop_constraint("fk_users_default_company", "users", schema=schema, type_="foreignkey")
        op.drop_column("users", "default_company_id", schema=schema)

    if _has_table("companies", schema):
        op.drop_table("companies", schema=schema)
