"""0002 — correction_factors + ref_consumption_rates (tabla CON)

Revision ID: 0002_correction_factors
Revises: 0001_initial
Create Date: 2026-07-06

Crea:
  - dcp_app.ref_consumption_rates  — consumos teóricos del Excel (hoja CON)
  - dcp_app.correction_factors     — factores de corrección auto-calibrados

Seed de ref_consumption_rates: datos extraídos de la hoja CON del archivo
Apro-PM 2026.ods (Ibérica, company_id=1).

Materiales en la tabla CON: harina, azucar, aceite, lecitina, sal
(carbonat y caramelina omitidos: consumos menores, no en silos principales)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_correction_factors"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── dcp_app.ref_consumption_rates ─────────────────────────────────────
    op.create_table(
        "ref_consumption_rates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_code", sa.String(length=32), nullable=False),
        sa.Column("material_type", sa.String(length=32), nullable=False),
        sa.Column("kg_per_batch", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_code", "material_type", "company_id", name="uq_ref_rate"),
        schema="dcp_app",
    )
    op.create_index("ix_ref_rates_recipe", "ref_consumption_rates", ["recipe_code", "company_id"], schema="dcp_app")

    # ── dcp_app.correction_factors ────────────────────────────────────────
    op.create_table(
        "correction_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("material_type", sa.String(length=32), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("stock_expected_kg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("stock_actual_kg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("consumption_theoretical_kg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("consumption_actual_kg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("factor", sa.Numeric(precision=6, scale=4), nullable=False, server_default="1.0"),
        sa.Column("source", sa.String(length=16), nullable=False, server_default="auto"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "material_type", "company_id", name="uq_correction_day"),
        schema="dcp_app",
    )
    op.create_index("ix_correction_date", "correction_factors", ["date", "material_type", "company_id"], schema="dcp_app")

    # ── Seed: hoja CON (Ibérica, company_id=1) ────────────────────────────
    # Datos extraídos de hoja CON del Apro-PM 2026.ods
    # Columnas originales mapeadas a recipe_code:
    #   STANDARD    → STANDARD
    #   STD S.S     → STANDARD_SS
    #   HASS 110    → HAAS_110
    #   HASS 98     → HAAS_98
    #   Mini 75 s.s.→ MINI_75_SS
    #   Mini 75 oli → MINI_75_OLI
    #   Mini 90 s.s.→ MINI_90_SS
    #   Mini 90     → MINI_90
    #   Imperial    → IMPERIAL
    #   Mini 82     → MINI_82
    #   Mini 82 Oreo→ MINI_82_OREO
    #   B.C.        → BC
    #
    # Materiales: harina, azucar, aceite, lecitina, sal
    # (kg por cuita = batch)

    op.execute("""
        INSERT INTO dcp_app.ref_consumption_rates
            (recipe_code, material_type, kg_per_batch, company_id)
        VALUES
            -- HARINA (kg/cuita)
            ('STANDARD',    'harina', 447,    1),
            ('STANDARD_SS', 'harina', 467,    1),
            ('HAAS_110',    'harina', 3501,   1),
            ('HAAS_98',     'harina', 3105,   1),
            ('MINI_75_SS',  'harina', 241,    1),
            ('MINI_75_OLI', 'harina', 224,    1),
            ('MINI_90_SS',  'harina', 377,    1),
            ('MINI_90',     'harina', 350,    1),
            ('IMPERIAL',    'harina', 473,    1),
            ('MINI_82',     'harina', 303,    1),
            ('MINI_82_OREO','harina', 269,    1),
            ('BC',          'harina', 447,    1),

            -- AZÚCAR (kg/cuita)
            ('STANDARD',    'azucar', 205,    1),
            ('STANDARD_SS', 'azucar', 0,      1),
            ('HAAS_110',    'azucar', 1587,   1),
            ('HAAS_98',     'azucar', 1408,   1),
            ('MINI_75_SS',  'azucar', 0,      1),
            ('MINI_75_OLI', 'azucar', 103,    1),
            ('MINI_90_SS',  'azucar', 0,      1),
            ('MINI_90',     'azucar', 161,    1),
            ('IMPERIAL',    'azucar', 218,    1),
            ('MINI_82',     'azucar', 140,    1),
            ('MINI_82_OREO','azucar', 135,    1),
            ('BC',          'azucar', 205,    1),

            -- ACEITE (kg/cuita)
            ('STANDARD',    'aceite', 22,     1),
            ('STANDARD_SS', 'aceite', 25,     1),
            ('HAAS_110',    'aceite', 185,    1),
            ('HAAS_98',     'aceite', 164,    1),
            ('MINI_75_SS',  'aceite', 13,     1),
            ('MINI_75_OLI', 'aceite', 38,     1),
            ('MINI_90_SS',  'aceite', 20,     1),
            ('MINI_90',     'aceite', 17,     1),
            ('IMPERIAL',    'aceite', 24,     1),
            ('MINI_82',     'aceite', 15,     1),
            ('MINI_82_OREO','aceite', 17,     1),
            ('BC',          'aceite', 22,     1),

            -- LECITINA (kg/cuita)
            ('STANDARD',    'lecitina', 10,   1),
            ('STANDARD_SS', 'lecitina', 11,   1),
            ('HAAS_110',    'lecitina', 79,   1),
            ('HAAS_98',     'lecitina', 70,   1),
            ('MINI_75_SS',  'lecitina', 6,    1),
            ('MINI_75_OLI', 'lecitina', 5,    1),
            ('MINI_90_SS',  'lecitina', 9,    1),
            ('MINI_90',     'lecitina', 7,    1),
            ('IMPERIAL',    'lecitina', 10,   1),
            ('MINI_82',     'lecitina', 6,    1),
            ('MINI_82_OREO','lecitina', 7,    1),
            ('BC',          'lecitina', 10,   1),

            -- SAL (kg/cuita)
            ('STANDARD',    'sal', 4,         1),
            ('STANDARD_SS', 'sal', 4,         1),
            ('HAAS_110',    'sal', 30,        1),
            ('HAAS_98',     'sal', 26,        1),
            ('MINI_75_SS',  'sal', 2,         1),
            ('MINI_75_OLI', 'sal', 2,         1),
            ('MINI_90_SS',  'sal', 3,         1),
            ('MINI_90',     'sal', 3,         1),
            ('IMPERIAL',    'sal', 4,         1),
            ('MINI_82',     'sal', 3,         1),
            ('MINI_82_OREO','sal', 3,         1),
            ('BC',          'sal', 4,         1)

        ON CONFLICT ON CONSTRAINT uq_ref_rate DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_table("correction_factors", schema="dcp_app")
    op.drop_table("ref_consumption_rates", schema="dcp_app")
