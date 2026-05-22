"""providers and changecase workflow

Revision ID: 0005_providers_and_changecase_workflow
Revises: 0004_watch_mode
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_providers_and_changecase_workflow'
down_revision = '0004_watch_mode'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('change_cases', sa.Column('planned_start', sa.DateTime(), nullable=True))
    op.add_column('change_cases', sa.Column('planned_end', sa.DateTime(), nullable=True))
    op.add_column('change_cases', sa.Column('change_type', sa.String(length=40), nullable=True))
    op.add_column('change_cases', sa.Column('affected_prefixes', sa.JSON(), nullable=True))
    op.add_column('change_cases', sa.Column('planned_origin_asns', sa.JSON(), nullable=True))
    op.add_column('change_cases', sa.Column('risk_summary', sa.Text(), nullable=True))
    op.add_column('change_cases', sa.Column('decision', sa.String(length=20), nullable=True))
    op.add_column('change_cases', sa.Column('required_actions', sa.JSON(), nullable=True))
    op.add_column('change_cases', sa.Column('post_change_status', sa.String(length=20), nullable=True))
    op.add_column('change_cases', sa.Column('last_preflight_at', sa.DateTime(), nullable=True))
    op.add_column('change_cases', sa.Column('last_verification_at', sa.DateTime(), nullable=True))
    op.add_column('watch_runs', sa.Column('alert_delivery_status', sa.String(length=30), nullable=True))
    op.add_column('watch_runs', sa.Column('alert_delivered_at', sa.DateTime(), nullable=True))
    op.add_column('watch_runs', sa.Column('alert_error_message', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('watch_runs', 'alert_error_message')
    op.drop_column('watch_runs', 'alert_delivered_at')
    op.drop_column('watch_runs', 'alert_delivery_status')
    for c in ['last_verification_at','last_preflight_at','post_change_status','required_actions','decision','risk_summary','planned_origin_asns','affected_prefixes','change_type','planned_end','planned_start']:
        op.drop_column('change_cases', c)
