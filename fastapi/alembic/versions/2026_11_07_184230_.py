"""empty message

Revision ID: 6ff05d37a0ed
Revises: e00c6a11384d, d51a9a4492b1
Create Date: 2026-11-07 18:42:30.711379+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ff05d37a0ed'
down_revision: Union[str, None] = ('e00c6a11384d', 'd51a9a4492b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
