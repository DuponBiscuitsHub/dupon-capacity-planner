"""add_historical_ml_tables

Revision ID: b21025bdaf67
Revises: 192025bdaf66
Create Date: 2026-06-04 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b21025bdaf67'
down_revision: Union[str, None] = '192025bdaf66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. dcp_app.silo_consumption_history
    op.create_table('silo_consumption_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('silo_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('initial_weight_kg', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('final_weight_kg', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('real_consumption_kg', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('theoretical_consumption_kg', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('ambient_temperature', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('ambient_humidity', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['odoo_replica.products.odoo_id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='dcp_app'
    )
    op.create_index(op.f('ix_dcp_app_silo_consumption_history_silo_id'), 'silo_consumption_history', ['silo_id'], unique=False, schema='dcp_app')
    op.create_index(op.f('ix_dcp_app_silo_consumption_history_timestamp'), 'silo_consumption_history', ['timestamp'], unique=False, schema='dcp_app')

    # 2. dcp_app.aluminum_operations_history
    op.create_table('aluminum_operations_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('machine_id', sa.Integer(), nullable=False),
    sa.Column('format_type', sa.String(length=32), nullable=False),
    sa.Column('quantity_processed_m2', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('scrap_produced_m2', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('real_downtime_minutes', sa.Integer(), nullable=False),
    sa.Column('maintenance_flag', sa.Boolean(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='dcp_app'
    )
    op.create_index(op.f('ix_dcp_app_aluminum_operations_history_machine_id'), 'aluminum_operations_history', ['machine_id'], unique=False, schema='dcp_app')
    op.create_index(op.f('ix_dcp_app_aluminum_operations_history_timestamp'), 'aluminum_operations_history', ['timestamp'], unique=False, schema='dcp_app')

    # 3. dcp_app.oven_throughput_history
    op.create_table('oven_throughput_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('workcenter_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('lot_quantity_packs', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('setup_time_minutes', sa.Integer(), nullable=False),
    sa.Column('real_baking_duration_hours', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('theoretical_duration_hours', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['odoo_replica.products.odoo_id'], ),
    sa.ForeignKeyConstraint(['workcenter_id'], ['odoo_replica.workcenters.odoo_id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='dcp_app'
    )
    op.create_index(op.f('ix_dcp_app_oven_throughput_history_timestamp'), 'oven_throughput_history', ['timestamp'], unique=False, schema='dcp_app')


def downgrade() -> None:
    op.drop_index(op.f('ix_dcp_app_oven_throughput_history_timestamp'), table_name='oven_throughput_history', schema='dcp_app')
    op.drop_table('oven_throughput_history', schema='dcp_app')
    
    op.drop_index(op.f('ix_dcp_app_aluminum_operations_history_timestamp'), table_name='aluminum_operations_history', schema='dcp_app')
    op.drop_index(op.f('ix_dcp_app_aluminum_operations_history_machine_id'), table_name='aluminum_operations_history', schema='dcp_app')
    op.drop_table('aluminum_operations_history', schema='dcp_app')
    
    op.drop_index(op.f('ix_dcp_app_silo_consumption_history_timestamp'), table_name='silo_consumption_history', schema='dcp_app')
    op.drop_index(op.f('ix_dcp_app_silo_consumption_history_silo_id'), table_name='silo_consumption_history', schema='dcp_app')
    op.drop_table('silo_consumption_history', schema='dcp_app')
