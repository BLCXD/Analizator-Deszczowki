"""Add administrator role to users."""
from alembic import op
import sqlalchemy as sa


revision = "20261024_admin_role"
down_revision = "20261024_user_profile"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column("users", "is_admin")
