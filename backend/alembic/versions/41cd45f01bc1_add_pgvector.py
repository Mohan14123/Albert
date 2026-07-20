"""Add pgvector to memories

Revision ID: 41cd45f01bc1
Revises: 34ed34f94fa0
Create Date: 2026-07-19 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "41cd45f01bc1"
down_revision: str | Sequence[str] | None = "34ed34f94fa0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure pgvector extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Drop embedding_id
    op.drop_column("memories", "embedding_id")

    # Add embedding vector column
    op.add_column("memories", sa.Column("embedding", Vector(1536), nullable=True))


def downgrade() -> None:
    op.drop_column("memories", "embedding")
    op.add_column(
        "memories", sa.Column("embedding_id", sa.String(length=255), nullable=True)
    )
    op.execute("DROP EXTENSION IF EXISTS vector")
