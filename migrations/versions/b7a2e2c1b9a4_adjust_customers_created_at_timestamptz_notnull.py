"""adjust customers.created_at to timestamptz and NOT NULL

Revision ID: b7a2e2c1b9a4
Revises: a6c0092c2b9f
Create Date: 2025-11-06 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b7a2e2c1b9a4"
down_revision: Union[str, Sequence[str], None] = "a6c0092c2b9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure no nulls before adding NOT NULL
    op.execute("UPDATE customers SET created_at = NOW() WHERE created_at IS NULL")
    # Change type to TIMESTAMP WITH TIME ZONE (timestamptz)
    op.alter_column(
        "customers",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(timezone=False),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    # Keep existing server default (now()) as defined in baseline; models use func.now()
    # Add NOT NULL constraint
    op.alter_column(
        "customers",
        "created_at",
        nullable=False,
        existing_nullable=True,
    )


def downgrade() -> None:
    # Remove NOT NULL
    op.alter_column(
        "customers",
        "created_at",
        nullable=True,
        existing_nullable=False,
    )
    # Server default unchanged in upgrade; no action needed here
    # Revert type back to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column(
        "customers",
        "created_at",
        type_=sa.DateTime(timezone=False),
        existing_type=sa.DateTime(timezone=True),
        postgresql_using="created_at",
    )
