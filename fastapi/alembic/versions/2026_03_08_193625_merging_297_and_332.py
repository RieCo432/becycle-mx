"""merging #297 and #332

Revision ID: 25b0de41df38
Revises: d4903d6a73db, 5b7b52dbd99c
Create Date: 2026-03-08 19:36:25.057856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25b0de41df38'
down_revision: Union[str, None] = ('d4903d6a73db', '5b7b52dbd99c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
