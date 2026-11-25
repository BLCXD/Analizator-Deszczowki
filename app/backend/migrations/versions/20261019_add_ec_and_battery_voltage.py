"""Add conductivity to measurements.

Revision ID: 20261019_ec_battery
Revises: add_measurement_id_001
Create Date: 2026-10-19
"""
from alembic import op
import sqlalchemy as sa
import uuid


revision = "20261019_ec_battery"
down_revision = "add_measurement_id_001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("measurements", sa.Column("ec", sa.Float(), nullable=True))
    connection = op.get_bind()
    missing_ids = connection.execute(sa.text("SELECT id FROM measurements WHERE measurement_id IS NULL")).fetchall()
    for row in missing_ids:
        connection.execute(
            sa.text("UPDATE measurements SET measurement_id = :measurement_id WHERE id = :id"),
            {"measurement_id": str(uuid.uuid4()), "id": row[0]},
        )
    with op.batch_alter_table("measurements") as batch_op:
        batch_op.alter_column("measurement_id", existing_type=sa.String(length=36), nullable=False)
        batch_op.create_index("ix_measurements_device_time", ["device_id", "measurement_time"], unique=False)


def downgrade():
    op.drop_column("measurements", "ec")
