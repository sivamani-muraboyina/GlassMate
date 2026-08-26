"""store application preparation snapshots

Revision ID: 8d9e0f1a2b3c
Revises: 7c8d9e0f1a2b
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d9e0f1a2b3c"
down_revision: Union[str, Sequence[str], None] = "7c8d9e0f1a2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("job_url_snapshot", sa.String(length=1000), nullable=True))
    op.add_column("applications", sa.Column("jd_snapshot", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("match_score", sa.Float(), nullable=True))
    op.add_column("applications", sa.Column("source", sa.String(length=100), nullable=True))
    op.execute("UPDATE applications SET job_url_snapshot = '', jd_snapshot = '', source = ''")
    op.alter_column("applications", "job_url_snapshot", nullable=False)
    op.alter_column("applications", "jd_snapshot", nullable=False)
    op.alter_column("applications", "source", nullable=False)


def downgrade() -> None:
    op.drop_column("applications", "source")
    op.drop_column("applications", "match_score")
    op.drop_column("applications", "jd_snapshot")
    op.drop_column("applications", "job_url_snapshot")