"""Add editable profile fields to users."""
from alembic import op
import sqlalchemy as sa


revision = "20261024_user_profile"
down_revision = "0002_add_push_subscriptions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=False, server_default=""))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=False, server_default=""))
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=False, server_default=""))


def downgrade():
    op.drop_column("users", "phone")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
