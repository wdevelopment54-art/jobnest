"""add site_settings table

Revision ID: a1b2c3d4e5f6
Revises: 10edbd4d9adc
Create Date: 2026-08-15 07:46:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '10edbd4d9adc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=80), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('label', sa.String(length=120), nullable=True),
        sa.Column('group', sa.String(length=40), nullable=False, server_default='general'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_site_settings_key', 'site_settings', ['key'], unique=True)


def downgrade():
    op.drop_index('ix_site_settings_key', table_name='site_settings')
    op.drop_table('site_settings')
