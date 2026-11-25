"""add measurement_id to measurements

Revision ID: add_measurement_id_001
Revises: f004729faa05
Create Date: 2026-10-02 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_measurement_id_001'
down_revision = 'f004729faa05'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('measurements', sa.Column('measurement_id', sa.String(length=36), nullable=True))
    with op.batch_alter_table('measurements', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_measurements_measurement_id', ['measurement_id'])


def downgrade():
    with op.batch_alter_table('measurements', schema=None) as batch_op:
        batch_op.drop_constraint('uq_measurements_measurement_id', type_='unique')
    op.drop_column('measurements', 'measurement_id')
