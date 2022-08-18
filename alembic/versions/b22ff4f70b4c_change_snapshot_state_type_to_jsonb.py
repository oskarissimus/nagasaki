"""change snapshot.state type to jsonb

Revision ID: b22ff4f70b4c
Revises:
Create Date: 2022-08-17 23:53:12.208383

"""
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from alembic import op

# revision identifiers, used by Alembic.
revision = "b22ff4f70b4c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "snapshot", "state", type_=pg.JSONB, postgresql_using="state::jsonb"
    )


def downgrade() -> None:
    op.alter_column("snapshot", "state", type_=sa.String)
