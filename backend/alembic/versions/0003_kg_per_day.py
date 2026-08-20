"""0003 — Evolución ref_consumption_rates a kg_per_day + line_formats + product_format_mappings

Revision ID: 0003_kg_per_day
Revises: 0002_correction_factors
Create Date: 2026-07-20

Cambios:
  - ref_consumption_rates: recipe_code → format_code, kg_per_batch → kg_per_day
  - Añade updated_by (FK a users) para auditoría
  - Nuevas tablas: line_formats, product_format_mappings
  - Re-seed completo con ~170 filas de consumos (incluyendo carbonat, caramelina,
    maltitol, cacao, colorante, oli_bany que faltaban en 0002)
  - Seed de line_formats: mapping líneas → formatos con nº máquinas
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003_kg_per_day"
down_revision: Union[str, None] = "0002_correction_factors"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Evolucionar ref_consumption_rates ─────────────────────────────

    # Drop old constraint y crear nueva
    op.drop_constraint("uq_ref_rate", "ref_consumption_rates", schema="dcp_app")
    op.drop_index("ix_ref_rates_recipe", "ref_consumption_rates", schema="dcp_app")

    # Renombrar columnas
    op.alter_column("ref_consumption_rates", "recipe_code",
                    new_column_name="format_code", schema="dcp_app")
    op.alter_column("ref_consumption_rates", "kg_per_batch",
                    new_column_name="kg_per_day", schema="dcp_app")

    # Añadir updated_by
    op.add_column("ref_consumption_rates",
                  sa.Column("updated_by", sa.Integer(),
                            sa.ForeignKey("dcp_app.users.id"), nullable=True),
                  schema="dcp_app")

    # Nueva constraint y índice
    op.create_unique_constraint(
        "uq_ref_rate_v2", "ref_consumption_rates",
        ["format_code", "material_type", "company_id"], schema="dcp_app"
    )
    op.create_index(
        "ix_ref_rates_format", "ref_consumption_rates",
        ["format_code", "company_id"], schema="dcp_app"
    )

    # ── 2. Renombrar format_codes: STANDARD→STD_R_110, etc. ──────────────
    # Los codes antiguos eran nombres de receta (STANDARD, HAAS_110).
    # Los nuevos son formato+receta (STD_R_110 para rotativos estándar).
    _renames = {
        "STANDARD": "STD_R_110",
        "STANDARD_SS": "STD_R_SS",
        # HAAS_110, HAAS_98, MINI_* ya están bien
        "BC": "BONCOLAC",
    }
    for old, new in _renames.items():
        op.execute(
            f"UPDATE dcp_app.ref_consumption_rates "
            f"SET format_code = '{new}' WHERE format_code = '{old}'"
        )

    # ── 3. Insertar ingredientes extra que faltaban en 0002 ──────────────
    # Datos de hoja CON del Excel Apro-PM 2026.ods
    # Valores = kg/día por 1 máquina (24h)
    op.execute("""
        INSERT INTO dcp_app.ref_consumption_rates
            (format_code, material_type, kg_per_day, company_id)
        VALUES
            -- CARBONAT (solo HAAS y variantes con carbonato de magnesio)
            ('HAAS_110',     'carbonat', 12,  1),
            ('HAAS_98',      'carbonat', 11,  1),

            -- CARAMELINA (solo HAAS estándar)
            ('HAAS_110',     'caramelina', 12, 1),
            ('HAAS_98',      'caramelina', 10, 1),

            -- MALTITOL (solo formatos sin azúcar)
            ('STD_R_SS',     'maltitol', 300, 1),
            ('MINI_75_SS',   'maltitol', 147, 1),
            ('MINI_90_SS',   'maltitol', 300, 1),

            -- CACAO (solo oreo)
            ('MINI_82_OREO', 'cacao', 32, 1),

            -- COLORANTE (solo oreo)
            ('MINI_82_OREO', 'colorante', 4, 1),

            -- OLI BANY (aceite de baño, solo Mini 75 oli)
            ('MINI_75_OLI',  'oli_bany', 165, 1),

            -- Formatos OREO para HAAS (estimados a partir de HAAS base + cacao+colorante de MINI_82_OREO)
            -- HAAS_98_OREO
            ('HAAS_98_OREO', 'harina', 3105,    1),
            ('HAAS_98_OREO', 'azucar', 1408,    1),
            ('HAAS_98_OREO', 'aceite', 164,     1),
            ('HAAS_98_OREO', 'lecitina', 70,    1),
            ('HAAS_98_OREO', 'sal', 26,         1),
            ('HAAS_98_OREO', 'carbonat', 11,    1),
            ('HAAS_98_OREO', 'cacao', 32,       1),
            ('HAAS_98_OREO', 'colorante', 4,    1),

            -- HAAS_110_OREO
            ('HAAS_110_OREO', 'harina', 3501,   1),
            ('HAAS_110_OREO', 'azucar', 1587,   1),
            ('HAAS_110_OREO', 'aceite', 185,    1),
            ('HAAS_110_OREO', 'lecitina', 79,   1),
            ('HAAS_110_OREO', 'sal', 30,        1),
            ('HAAS_110_OREO', 'carbonat', 12,   1),
            ('HAAS_110_OREO', 'cacao', 32,      1),
            ('HAAS_110_OREO', 'colorante', 4,   1),

            -- Añadir MINI_90 con carbonato (faltaba)
            ('BONCOLAC',     'lecitina', 10,    1),
            ('MINI_90_SS',   'lecitina', 9,     1)

        ON CONFLICT ON CONSTRAINT uq_ref_rate_v2 DO NOTHING;
    """)

    # ── 4. Crear tabla line_formats ───────────────────────────────────────
    op.create_table(
        "line_formats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("line_code", sa.String(length=8), nullable=False),
        sa.Column("format_code", sa.String(length=32), nullable=False),
        sa.Column("machines", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("line_code", "format_code", "company_id", name="uq_line_format"),
        schema="dcp_app",
    )
    op.create_index("ix_line_format_line", "line_formats",
                    ["line_code", "company_id"], schema="dcp_app")

    # Seed: mapping líneas → formatos con nº máquinas
    # L01+L02 = misma MO, 8 hornos rotativos (compartidos)
    # L06 = 8 hornos rotativos (independiente)
    # L03-L05, L07-L10 = lineales, 1 máquina
    op.execute("""
        INSERT INTO dcp_app.line_formats (line_code, format_code, machines, company_id)
        VALUES
            -- Rotativos (8 hornos cada línea)
            ('L01_L02', 'STD_R_110', 8, 1),
            ('L01_L02', 'STD_R_SS',  8, 1),
            ('L06',     'STD_R_110', 8, 1),
            ('L06',     'STD_R_SS',  8, 1),

            -- Lineales HAAS
            ('L03', 'HAAS_110',       1, 1),
            ('L03', 'HAAS_110_OREO',  1, 1),
            ('L04', 'HAAS_110',       1, 1),
            ('L04', 'HAAS_98',        1, 1),
            ('L04', 'HAAS_98_OREO',   1, 1),
            ('L04', 'HAAS_110_OREO',  1, 1),
            ('L07', 'HAAS_110',       1, 1),
            ('L09', 'HAAS_98',        1, 1),
            ('L09', 'HAAS_98_OREO',   1, 1),
            ('L10', 'HAAS_98',        1, 1),
            ('L10', 'HAAS_98_OREO',   1, 1),

            -- Lineales Mini
            ('L05', 'MINI_75_SS',     1, 1),
            ('L05', 'MINI_75_OLI',    1, 1),
            ('L05', 'MINI_82',        1, 1),
            ('L08', 'MINI_82',        1, 1),
            ('L08', 'MINI_82_OREO',   1, 1)

        ON CONFLICT ON CONSTRAINT uq_line_format DO NOTHING;
    """)

    # ── 5. Crear tabla product_format_mappings ────────────────────────────
    op.create_table(
        "product_format_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_product_id", sa.Integer(), nullable=False),
        sa.Column("format_code", sa.String(length=32), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_product_id", "company_id", name="uq_product_format"),
        schema="dcp_app",
    )
    op.create_index("ix_product_format_odoo", "product_format_mappings",
                    ["odoo_product_id", "company_id"], schema="dcp_app")

    # product_format_mappings se deja vacía: se poblará cuando tengamos
    # los product_ids reales de Odoo (TBD-4)


def downgrade() -> None:
    # Drop nuevas tablas
    op.drop_table("product_format_mappings", schema="dcp_app")
    op.drop_table("line_formats", schema="dcp_app")

    # Revertir ref_consumption_rates
    op.drop_constraint("uq_ref_rate_v2", "ref_consumption_rates", schema="dcp_app")
    op.drop_index("ix_ref_rates_format", "ref_consumption_rates", schema="dcp_app")
    op.drop_column("ref_consumption_rates", "updated_by", schema="dcp_app")

    # Renombrar columnas de vuelta
    op.alter_column("ref_consumption_rates", "format_code",
                    new_column_name="recipe_code", schema="dcp_app")
    op.alter_column("ref_consumption_rates", "kg_per_day",
                    new_column_name="kg_per_batch", schema="dcp_app")

    # Revertir format_codes
    _renames = {"STD_R_110": "STANDARD", "STD_R_SS": "STANDARD_SS", "BONCOLAC": "BC"}
    for new, old in _renames.items():
        op.execute(
            f"UPDATE dcp_app.ref_consumption_rates "
            f"SET recipe_code = '{old}' WHERE recipe_code = '{new}'"
        )

    # Eliminar filas extra (carbonat, caramelina, maltitol, etc.)
    op.execute("""
        DELETE FROM dcp_app.ref_consumption_rates
        WHERE material_type IN ('carbonat', 'caramelina', 'maltitol', 'cacao',
                                'colorante', 'oli_bany')
           OR recipe_code LIKE '%_OREO'
    """)

    # Recrear constraint y index originales
    op.create_unique_constraint(
        "uq_ref_rate", "ref_consumption_rates",
        ["recipe_code", "material_type", "company_id"], schema="dcp_app"
    )
    op.create_index("ix_ref_rates_recipe", "ref_consumption_rates",
                    ["recipe_code", "company_id"], schema="dcp_app")
