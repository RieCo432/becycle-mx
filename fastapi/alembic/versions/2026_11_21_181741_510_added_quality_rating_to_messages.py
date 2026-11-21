"""#510 A-8 add messages.qualityrating (AI reply quality rating)

Revision ID: e4a7c2b9d5f1
Revises: 707389612f50
Create Date: 2026-11-21 18:17:41

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4a7c2b9d5f1'
down_revision: Union[str, None] = '707389612f50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # #510 A-8: the staff quality rating of an AI reply, set in the audit
    # trail: true = good, false = not good, null = not yet rated. Nullable —
    # human messages and unrated AI replies have no rating.
    op.add_column('messages', sa.Column('qualityrating', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'qualityrating')
