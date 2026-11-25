"""Remove the unsupported tank-level measurement."""
from alembic import op


revision = "20261022_remove_level"
down_revision = "20261021_rainfall"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("measurements") as batch:
        batch.drop_column("water_level")


def downgrade():
    raise RuntimeError("The removed water-level readings cannot be restored")
