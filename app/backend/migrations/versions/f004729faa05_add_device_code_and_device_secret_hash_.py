"""Add device_code and device_secret_hash to device

Revision ID: f004729faa05
Revises: c46c44d0c45c
Create Date: 2026-10-02 22:26:12.377123

"""
from alembic import op
import sqlalchemy as sa

revision = 'f004729faa05'
down_revision = 'c46c44d0c45c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('devices', sa.Column('device_code', sa.String(), nullable=True))
    op.add_column('devices', sa.Column('device_secret_hash', sa.String(), nullable=True))
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_devices_device_code', ['device_code'])


def downgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_constraint('uq_devices_device_code', type_='unique')
    op.drop_column('devices', 'device_secret_hash')
    op.drop_column('devices', 'device_code')
