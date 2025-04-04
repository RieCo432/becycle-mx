"""added about us table

Revision ID: a3e4a6ebae58
Revises: 06664d6761d8
Create Date: 2025-03-16 15:33:49.069834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3e4a6ebae58'
down_revision: Union[str, None] = '06664d6761d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    about_us_table = op.create_table('aboutus',
    sa.Column('id', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('html', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aboutus_id'), 'aboutus', ['id'], unique=False)
    op.bulk_insert(about_us_table,[{"id": 1, "html": "<h1>Hello There</p>"}])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_aboutus_id'), table_name='aboutus')
    op.drop_table('aboutus')
    # ### end Alembic commands ###
