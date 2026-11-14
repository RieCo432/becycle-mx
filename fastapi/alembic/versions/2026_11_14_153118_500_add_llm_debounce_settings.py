"""#500 add LLM debounce settings to llmsettings

Revision ID: c6341d917c09
Revises: 6bce1001cca9
Create Date: 2026-11-14 15:31:18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6341d917c09'
down_revision: Union[str, None] = '6bce1001cca9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The Agent harness debounce policy (#500 H-6): the silence window (seconds)
    # and the max messages per batch. Editable via the LLM settings UI; read
    # per message so admin edits apply live. Seeded with defaults.
    op.add_column('llmsettings', sa.Column('debouncewindowseconds', sa.Integer(), nullable=False, server_default=sa.text('30')))
    op.add_column('llmsettings', sa.Column('debouncebatchcap', sa.Integer(), nullable=False, server_default=sa.text('6')))


def downgrade() -> None:
    op.drop_column('llmsettings', 'debouncebatchcap')
    op.drop_column('llmsettings', 'debouncewindowseconds')
