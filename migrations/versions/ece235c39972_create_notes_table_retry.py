"""create notes table (retry)

Revision ID: ece235c39972
Revises: c1e2f3a4b5c6
Create Date: 2025-11-06 16:16:15.815068

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ece235c39972"
down_revision: Union[str, Sequence[str], None] = "c1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create notes table if it doesn't already exist."""
    # Use raw SQL to check if table exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes')"
        )
    )
    table_exists = result.scalar()

    if not table_exists:
        op.create_table(
            "notes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("customer_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name=op.f("fk_notes_customer_id_customers"),
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name=op.f("fk_notes_user_id_users"),
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_notes")),
        )
        op.create_index(op.f("ix_notes_id"), "notes", ["id"], unique=False)


def downgrade() -> None:
    """Drop notes table."""
    op.drop_index(op.f("ix_notes_id"), table_name="notes")
    op.drop_table("notes")
