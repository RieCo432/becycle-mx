"""merge heads

Revision ID: 0d1bebf23705
Revises: 289ab654eaa9, 9426f1d0102e
Create Date: 2026-08-22 14:00:16.268060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d1bebf23705'
down_revision: Union[str, None] = ('289ab654eaa9', '9426f1d0102e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
