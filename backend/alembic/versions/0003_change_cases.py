"""add change cases

Revision ID: 0003_change_cases
Revises: 0002_users_and_report_ownership
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_change_cases'
down_revision = '0002_users_and_report_ownership'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('change_cases',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.add_column('checks', sa.Column('change_case_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_checks_change_case_id', 'checks', 'change_cases', ['change_case_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_checks_change_case_id', 'checks', type_='foreignkey')
    op.drop_column('checks', 'change_case_id')
    op.drop_table('change_cases')
