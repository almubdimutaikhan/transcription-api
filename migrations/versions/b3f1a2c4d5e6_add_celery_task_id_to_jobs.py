"""add celery_task_id to jobs

Revision ID: b3f1a2c4d5e6
Revises: 46a9632e2c00
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b3f1a2c4d5e6'
down_revision: Union[str, Sequence[str], None] = '46a9632e2c00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transcription_jobs', sa.Column('celery_task_id', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('transcription_jobs', 'celery_task_id')
