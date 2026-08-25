"""enforce resume version numbering

Revision ID: 6f5c2d9b4e11
Revises: 4a4c0631f170
Create Date: 2026-08-25
"""
from typing import Sequence, Union

from alembic import op


revision: str = "6f5c2d9b4e11"
down_revision: Union[str, Sequence[str], None] = "4a4c0631f170"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_resume_versions_resume_number",
        "resume_versions",
        ["resume_id", "version_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_resume_versions_resume_number",
        "resume_versions",
        type_="unique",
    )
