"""placeholder initial revision to bridge staging DB

Revision ID: d6201c8b3178
Revises:
Create Date: 2025-11-06 16:35:00

This migration intentionally performs no schema changes. It exists to align
the database's recorded Alembic version with the current migration history
in this repository. Staging databases that report this revision can now
advance to newer revisions defined here.
"""

from alembic import op  # noqa: F401  (kept for consistency)
import sqlalchemy as sa  # noqa: F401  (kept for consistency)


# revision identifiers, used by Alembic.
revision = "d6201c8b3178"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op: placeholder bridge migration."""
    pass


def downgrade() -> None:
    """No-op: placeholder bridge migration."""
    pass
