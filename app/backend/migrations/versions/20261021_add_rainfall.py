"""Store cumulative and hourly rainfall readings."""
from alembic import op
import sqlalchemy as sa


revision = "20261021_rainfall"
down_revision = "20261020_password_reset"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("measurements", sa.Column("rainfall_mm", sa.Float(), nullable=True))
    op.add_column("measurements", sa.Column("rainfall_1h_mm", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("measurements", "rainfall_1h_mm")
    op.drop_column("measurements", "rainfall_mm")
