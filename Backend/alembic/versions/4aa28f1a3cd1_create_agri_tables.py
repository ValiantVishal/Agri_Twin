"""create_agri_tables

Revision ID: 4aa28f1a3cd1
Revises: 
Create Date: 2026-08-01 06:29:30.131277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4aa28f1a3cd1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True, unique=True),
        sa.Column('password', sa.String(length=255), nullable=True)
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Farmer Profiles Table
    op.create_table(
        'farmer_profiles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True, unique=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('village', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('farmer_type', sa.String(length=100), nullable=True),
        sa.Column('experience', sa.Integer(), nullable=True),
        sa.Column('crop', sa.String(length=100), nullable=True),
        sa.Column('irrigation', sa.String(length=100), nullable=True),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index(op.f('ix_farmer_profiles_id'), 'farmer_profiles', ['id'], unique=False)

    # 3. Plots Table
    op.create_table(
        'plots',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.Column('plot_name', sa.String(length=100), nullable=False),
        sa.Column('points', sa.JSON(), nullable=False),
        sa.Column('area_sqm', sa.Float(), nullable=False),
        sa.Column('area_acres', sa.Float(), nullable=False),
        sa.Column('area_cents', sa.Float(), nullable=False),
        sa.Column('perimeter_m', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id'], )
    )
    op.create_index(op.f('ix_plots_id'), 'plots', ['id'], unique=False)

    # 4. Activity Logs Table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.Column('plot_id', sa.String(length=36), nullable=True),
        sa.Column('entry_text', sa.String(), nullable=False),
        sa.Column('entry_language', sa.String(length=10), nullable=False),
        sa.Column('input_mode', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], )
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')
    op.drop_index(op.f('ix_plots_id'), table_name='plots')
    op.drop_table('plots')
    op.drop_index(op.f('ix_farmer_profiles_id'), table_name='farmer_profiles')
    op.drop_table('farmer_profiles')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
