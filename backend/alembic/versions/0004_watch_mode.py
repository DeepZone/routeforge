"""watch mode

Revision ID: 0004_watch_mode
Revises: 0003_change_cases
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_watch_mode'
down_revision = '0003_change_cases'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'watch_targets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('watch_type', sa.String(length=30), nullable=False),
        sa.Column('prefix', sa.String(length=120), nullable=True),
        sa.Column('asn', sa.String(length=20), nullable=True),
        sa.Column('origin_as', sa.String(length=20), nullable=True),
        sa.Column('expected_origin_as', sa.String(length=20), nullable=True),
        sa.Column('max_length', sa.Integer(), nullable=True),
        sa.Column('interval_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('change_case_id', sa.Integer(), sa.ForeignKey('change_cases.id'), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_watch_targets_id'), 'watch_targets', ['id'])

    op.create_table(
        'watch_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('watch_target_id', sa.Integer(), sa.ForeignKey('watch_targets.id'), nullable=False),
        sa.Column('report_id', sa.Integer(), sa.ForeignKey('reports.id'), nullable=True),
        sa.Column('previous_status', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('changed', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_watch_runs_id'), 'watch_runs', ['id'])

def downgrade() -> None:
    op.drop_index(op.f('ix_watch_runs_id'), table_name='watch_runs')
    op.drop_table('watch_runs')
    op.drop_index(op.f('ix_watch_targets_id'), table_name='watch_targets')
    op.drop_table('watch_targets')
