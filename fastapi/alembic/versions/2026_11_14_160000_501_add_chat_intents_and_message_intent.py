"""#501 add chat_intents table, seed intents, and the messages.intent column

Revision ID: 5f8c2d91a3b7
Revises: c6341d917c09
Create Date: 2026-11-14 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f8c2d91a3b7'
down_revision: Union[str, None] = 'c6341d917c09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # #501: the per-org client-chat intent set (C-9). Each row is a classified
    # route the Agent dispatches to: `name` is the classifier's slug + dispatch key,
    # `whentouse` feeds the classification prompt, `replytemplate` is the pre-formed
    # reply (may reference live-data fragments like {{open_today}}), `enabled`
    # soft-disables a row, `orderindex` is the display/classify order.
    chat_intents_table = op.create_table('chat_intents',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('whentouse', sa.Text(), nullable=True),
    sa.Column('replytemplate', sa.Text(), nullable=False),
    sa.Column('enabled', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
    sa.Column('orderindex', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_intents_id'), 'chat_intents', ['id'], unique=False)
    op.create_index(op.f('ix_chat_intents_name'), 'chat_intents', ['name'], unique=True)

    # Seed the initial intent set. Templates are org-agnostic (this code serves
    # multiple shops); the dynamic bits come from the referenced fragments, which
    # are computed from each shop's own data at call time.
    op.bulk_insert(chat_intents_table, [
        {
            "name": "open_today",
            "whentouse": "Asks whether the workshop is open today or right now.",
            "replytemplate": "{{open_today}}",
            "enabled": True,
            "orderindex": 0,
        },
        {
            "name": "hours",
            "whentouse": "Asks what the workshop's opening hours are (the weekly schedule).",
            "replytemplate": "We're open {{opening_hours}}.",
            "enabled": True,
            "orderindex": 1,
        },
        {
            "name": "booking",
            "whentouse": "Wants to book or schedule an appointment to visit the workshop.",
            "replytemplate": "To book an appointment, please use the Book Appointment function.",
            "enabled": True,
            "orderindex": 2,
        },
        {
            "name": "repair_request",
            "whentouse": "Says something is wrong with their bike and wants it fixed or looked at.",
            "replytemplate": ("For a repair, book an appointment using the Book Appointment function. "
                              "If you're not sure what to book, book an inspection — or try your luck by "
                              "dropping in without an appointment for us to do an inspection and get you "
                              "booked in."),
            "enabled": True,
            "orderindex": 3,
        },
        {
            "name": "parts_inquiry",
            "whentouse": "Asks whether the workshop has a part in stock, or about getting a part.",
            "replytemplate": "Come in during our opening hours and a volunteer can check what parts we have in stock for your bike.",
            "enabled": True,
            "orderindex": 4,
        },
    ])

    # #501 C-7: record which intent a client auto-reply was produced for (audit).
    # Plain label, no FK: an intent can be renamed/removed later without breaking
    # replies that already recorded it. Nullable — human messages and volunteer
    # free-form replies have no intent.
    op.add_column('messages', sa.Column('intent', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'intent')
    op.drop_index(op.f('ix_chat_intents_name'), table_name='chat_intents')
    op.drop_index(op.f('ix_chat_intents_id'), table_name='chat_intents')
    op.drop_table('chat_intents')
