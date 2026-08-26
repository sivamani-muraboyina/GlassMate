"""store resume proposal provenance

Revision ID: 7c8d9e0f1a2b
Revises: 343f6b758676
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c8d9e0f1a2b"
down_revision: Union[str, Sequence[str], None] = "343f6b758676"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "resume_versions",
        sa.Column("source_version_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_resume_versions_source_version_id",
        "resume_versions",
        "resume_versions",
        ["source_version_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_resume_versions_source_version_id",
        "resume_versions",
        type_="foreignkey",
    )
    op.drop_column("resume_versions", "source_version_id")