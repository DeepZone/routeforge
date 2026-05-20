"""users and report ownership

Revision ID: 0002_users_and_report_ownership
Revises: 0001_initial_schema
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_users_and_report_ownership"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    with op.batch_alter_table("checks") as batch:
        batch.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_checks_created_by_user_id", "users", ["created_by_user_id"], ["id"])
    with op.batch_alter_table("reports") as batch:
        batch.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_reports_created_by_user_id", "users", ["created_by_user_id"], ["id"])
    op.create_table("audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=True),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

def downgrade() -> None:
    op.drop_table("audit_log")
    with op.batch_alter_table("reports") as batch:
        batch.drop_constraint("fk_reports_created_by_user_id", type_="foreignkey")
        batch.drop_column("created_by_user_id")
    with op.batch_alter_table("checks") as batch:
        batch.drop_constraint("fk_checks_created_by_user_id", type_="foreignkey")
        batch.drop_column("created_by_user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
