"""create packages table

Revision ID: create_packages_table
Revises: create_invoices_table
Create Date: 2024-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_packages_table'
down_revision = 'create_invoices_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('interval', sa.String(), nullable=False),
        sa.Column('trial_days', sa.Integer(), nullable=True),
        sa.Column('max_projects', sa.Integer(), nullable=False),
        sa.Column('features', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('button_text', sa.String(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_packages_name'), 'packages', ['name'], unique=True)
    op.create_index(op.f('ix_packages_id'), 'packages', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_packages_name'), table_name='packages')
    op.drop_index(op.f('ix_packages_id'), table_name='packages')
    op.drop_table('packages')
