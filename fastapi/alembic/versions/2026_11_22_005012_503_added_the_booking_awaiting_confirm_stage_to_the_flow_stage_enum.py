"""#503 added the booking_awaiting_confirm stage to the flow stage enum

Revision ID: b7e2f4a91c33
Revises: 8c1d56aa88d5
Create Date: 2026-11-22 00:50:12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7e2f4a91c33'
down_revision = '8c1d56aa88d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Native enum types are only created/dropped by SQLAlchemy via the
    # create_table/drop_table events (named_types.py) - adding a value is not
    # something autogenerate emits at all, so this goes through raw SQL
    # (the #299 pattern). NOTE: SQLAlchemy persists the enum MEMBER NAMES
    # (see the created labels BOOKING_ELICITING / BOOKING_AWAITING_SLOT_CHOICE),
    # not the Python values - use the uppercase name, not "booking_awaiting_confirm".
    # Postgres 12+ allows ADD VALUE inside a transaction (the server here is 16, compose.yaml).
    db = op.get_bind()
    db.execute(sa.text("ALTER TYPE chatactionflowstage ADD VALUE 'BOOKING_AWAITING_CONFIRM';"))


def downgrade() -> None:
    # DROP VALUE is Postgres 12+ (only possible while the value is unused).
    db = op.get_bind()
    db.execute(sa.text("ALTER TYPE chatactionflowstage DROP VALUE 'BOOKING_AWAITING_CONFIRM';"))
