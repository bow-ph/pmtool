"""create hint confirmations table

Revision ID: 2024_02_01_create_hint_confirmations
Revises: ed7f10d4b070
Create Date: 2024-02-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2024_02_01_create_hint_confirmations'
down_revision: Union[str, None] = 'ed7f10d4b070'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'hint_confirmations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('hint_message', sa.String(), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('confirmed_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['confirmed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hint_confirmations_id'), 'hint_confirmations', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_hint_confirmations_id'), table_name='hint_confirmations')
    op.drop_table('hint_confirmations')
