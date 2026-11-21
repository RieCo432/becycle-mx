"""#511 added the ai disclosure to the llm settings (public "About our AI" policy)

Revision ID: f3a9c1d57e20
Revises: e4a7c2b9d5f1
Create Date: 2026-11-21 19:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f3a9c1d57e20'
down_revision: Union[str, None] = 'e4a7c2b9d5f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# #511 D-8: the seeded default policy. Plain Markdown, org-neutral (each shop
# can edit it through the LLM Settings page). Covers the current scope of AI
# use: customer intent classification, staff free-form replies (with live
# feed-in of the shop's own data), and the appointment booking assistant.
DEFAULT_DISCLOSURE = """\
# How we use AI

We are a volunteer-run bike workshop, and we use AI in a few small, specific ways to make life easier for our volunteers and the community. This page tells you where you will meet it, what it can see, and what to expect.

## If you are a customer

**Your chat with us.** Our volunteers used to spend a lot of their time answering the same questions again and again. To help with that, an AI model now reads each message you send and works out what you are asking about. If your question is one we answer often, you will receive a pre-prepared reply straight away. If your question is more specific, or does not fit one of the recognised topics, the AI will not respond and a volunteer will get back to you. This means common questions are answered faster, and our volunteers can spend more of their time fixing bikes.

**Booking appointments.** If you want to book an appointment, the assistant walks you through a short conversation: what you need, which kind of appointment fits, and which times are actually free. The slot you choose becomes a normal appointment request in our booking system, and you will also receive an email confirmation as usual.

**What to be aware of.**

- Our AI is self-hosted, like the rest of this website: your messages are not sent to any third party. Even so, please do not share sensitive details such as bank or ID numbers.
- A human volunteer makes the final call on everything that affects you: repairs, payments, and confirmed bookings.

**What to expect.**

- A booking you confirm with the assistant is a normal workshop appointment request, which you can change or cancel, and which is manually approved by us as usual.

## If you are a volunteer

**The staff assistant.** You can chat with the assistant about work. There it will answer in free form, and it sees a live slice of the shop's own data (for example current opening hours and appointment availability), so its answers reflect what is actually true at that moment.

**What to be aware of.**

- AI can be wrong. Treat assistant answers (especially free-form answers and anything about availability) as a helpful first pass, not as fact.
- You make the final call on everything the assistant does in the shop.

## For everyone

- Our use of AI may grow over time. When it does, this page will say what is new and why.
- You can reach this page at any time from the "AI" badge on any assistant reply in the chat.
"""


def upgrade() -> None:
    op.add_column('llmsettings', sa.Column('aidisclosure', sa.Text(), nullable=True))
    # op.execute() in this Alembic version does not accept bind parameters,
    # so seed through the migration's own connection (the #309 pattern).
    db = op.get_bind()
    db.execute(
        sa.text("UPDATE llmsettings SET aidisclosure = :content WHERE id = 1"),
        {"content": DEFAULT_DISCLOSURE},
    )


def downgrade() -> None:
    op.drop_column('llmsettings', 'aidisclosure')
