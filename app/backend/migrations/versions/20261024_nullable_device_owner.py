"""Allow devices to remain after their owner account is deleted."""
from alembic import op
import sqlalchemy as sa


revision = "20261024_nullable_device_owner"
down_revision = "20261024_admin_role"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("devices", "user_id", existing_type=sa.Integer(), nullable=True)


def downgrade():
    op.alter_column("devices", "user_id", existing_type=sa.Integer(), nullable=False)
