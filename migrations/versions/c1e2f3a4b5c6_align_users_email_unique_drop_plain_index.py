"""Align users.email uniqueness and drop plain index

Revision ID: c1e2f3a4b5c6
Revises: b7a2e2c1b9a4
Create Date: 2025-11-06 00:00:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "b7a2e2c1b9a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure users.email has a UNIQUE constraint and drop redundant non-unique index."""
    # Drop the plain index if it exists
    op.execute("DROP INDEX IF EXISTS ix_users_email")

    # Add a named UNIQUE constraint on users(email) if it doesn't already exist
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE c.contype = 'u'
                  AND t.relname = 'users'
                  AND n.nspname = current_schema()
                  AND (
                    SELECT string_agg(a.attname, ',')
                    FROM unnest(c.conkey) AS cols
                    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = cols
                  ) = 'email'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    """Recreate the plain index and drop the named UNIQUE constraint (if present)."""
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_email")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
