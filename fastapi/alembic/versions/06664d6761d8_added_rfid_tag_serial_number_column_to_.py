"""added RFID tag serial number column to bikes table

Revision ID: 06664d6761d8
Revises: bed4d97ffb44
Create Date: 2025-02-23 15:38:51.015411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06664d6761d8'
down_revision: Union[str, None] = 'bed4d97ffb44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bikes', sa.Column('rfidtagserialnumber', sa.String(length=24), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bikes', 'rfidtagserialnumber')
    # ### end Alembic commands ###
