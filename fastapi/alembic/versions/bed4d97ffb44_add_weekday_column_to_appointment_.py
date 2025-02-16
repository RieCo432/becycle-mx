"""add weekday column to appointment concurrency limits

Revision ID: bed4d97ffb44
Revises: 2b1bf0903a94
Create Date: 2025-02-15 20:13:49.749023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bed4d97ffb44'
down_revision: Union[str, None] = '2b1bf0903a94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('appointmentconcurrencylimits', sa.Column('weekday', sa.Integer(), nullable=False, server_default='0'))
    op.alter_column('appointmentconcurrencylimits', 'weekday', server_default=None)
    op.create_index(op.f('ix_appointmentconcurrencylimits_weekday'), 'appointmentconcurrencylimits', ['weekday'], unique=False)
    op.drop_constraint('appointmentconcurrencylimits_pkey', 'appointmentconcurrencylimits')
    op.create_primary_key('appointmentconcurrencylimits_pkey', 'appointmentconcurrencylimits', ['weekday', 'aftertime'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM appointmentconcurrencylimits WHERE weekday!=0;")
    op.drop_constraint('appointmentconcurrencylimits_pkey', 'appointmentconcurrencylimits')
    op.drop_index(op.f('ix_appointmentconcurrencylimits_weekday'), table_name='appointmentconcurrencylimits')
    op.drop_column('appointmentconcurrencylimits', 'weekday')
    op.create_primary_key('appointmentconcurrencylimits_pkey', 'appointmentconcurrencylimits', ['aftertime'])
    # ### end Alembic commands ###
