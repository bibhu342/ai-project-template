"""add_indexes_to_notes_table

Revision ID: 2f387382491d
Revises: ece235c39972
Create Date: 2025-11-06 18:00:21.770736

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2f387382491d"
down_revision: Union[str, Sequence[str], None] = "ece235c39972"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add indexes for common query patterns on notes table
    op.create_index("ix_notes_customer_id", "notes", ["customer_id"], unique=False)
    op.create_index("ix_notes_user_id", "notes", ["user_id"], unique=False)
    op.create_index("ix_notes_created_at", "notes", ["created_at"], unique=False)
    # Composite index for common query: notes by customer, ordered by date
    op.create_index(
        "ix_notes_customer_created",
        "notes",
        ["customer_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes in reverse order
    op.drop_index("ix_notes_customer_created", table_name="notes")
    op.drop_index("ix_notes_created_at", table_name="notes")
    op.drop_index("ix_notes_user_id", table_name="notes")
    op.drop_index("ix_notes_customer_id", table_name="notes")
