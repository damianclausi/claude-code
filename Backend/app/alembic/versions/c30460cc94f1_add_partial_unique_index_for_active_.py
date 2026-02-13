"""add partial unique index for active ratings

Revision ID: c30460cc94f1
Revises: 0e3a8766f785
Create Date: 2026-02-13 00:20:51.708505

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'c30460cc94f1'
down_revision: Union[str, None] = '0e3a8766f785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add partial unique index for active ratings (deleted_at IS NULL)."""
    op.create_index(
        'uix_course_ratings_active_user_course',
        'course_ratings',
        ['course_id', 'user_id'],
        unique=True,
        postgresql_where=text("deleted_at IS NULL")
    )


def downgrade() -> None:
    """Remove partial unique index for active ratings."""
    op.drop_index(
        'uix_course_ratings_active_user_course',
        table_name='course_ratings'
    )
