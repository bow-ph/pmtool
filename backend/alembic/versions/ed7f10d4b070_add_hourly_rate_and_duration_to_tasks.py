"""add_hourly_rate_and_duration_to_tasks

Revision ID: ed7f10d4b070
Revises: 2453de19b08e
Create Date: 2025-02-01 10:38:41.848453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed7f10d4b070'
down_revision: Union[str, None] = '2453de19b08e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('hourly_rate', sa.Float(), nullable=True))
    op.add_column('tasks', sa.Column('duration_hours', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'duration_hours')
    op.drop_column('tasks', 'hourly_rate')
