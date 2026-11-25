"""Create measurement table

Revision ID: c46c44d0c45c
Revises: bd5449844be2
Create Date: 2026-10-02 21:59:00.897029

"""
from alembic import op
import sqlalchemy as sa
revision = 'c46c44d0c45c'
down_revision = 'bd5449844be2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('water_level', sa.Float(), nullable=False),
        sa.Column('water_quality_turbidity', sa.Float(), nullable=True),
        sa.Column('water_quality_ph', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('measurement_time', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('raw_data', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('measurements')
