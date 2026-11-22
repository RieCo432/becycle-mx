"""#503 fixed the stale classification prompt seed and broadened the booking intent routing

Revision ID: c9d3e5b17f42
Revises: b7e2f4a91c33
Create Date: 2026-11-22 01:08:15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c9d3e5b17f42'
down_revision = 'b7e2f4a91c33'
branch_labels = None
depends_on = None

# The #482 seed: a hardcoded closed set that predates the open_today / hours
# intents, and an "other" option that _extract_intent degrades to "none" -
# so messages like "I want to rent a bike" were classified "none" (silence)
# instead of "booking". Verified against the live model: clearing it (so the
# code default applies - the real closed set is always appended by classify)
# plus the broadened booking row below routes all the rental phrasings to
# "booking".
OLD_CLASSIFICATION_PROMPT = (
    "You are a message classifier, not a conversational assistant. "
    "Do not answer the customer. Classify their latest message into exactly one "
    "intent: repair_request, booking, parts_inquiry, other. Respond with JSON "
    'only: {"intent": "<one of the above>"}'
)
OLD_BOOKING_WHENTOUSE = "Wants to book or schedule an appointment to visit the workshop."
NEW_BOOKING_WHENTOUSE = (
    "Wants to book, schedule, or reserve any appointment or workshop service - "
    "including specific requests such as 'I want a repair', 'I need an "
    "inspection', or 'I want to rent / loan a bike' (these are all booked as "
    "appointments)."
)


def upgrade() -> None:
    db = op.get_bind()
    # Guarded: only the verbatim seed is cleared, so an admin who has since
    # overridden the classification prompt (LlmSettings update) is not clobbered.
    db.execute(
        sa.text("UPDATE llmsettings SET classificationprompt = NULL "
                "WHERE classificationprompt = :old"),
        {"old": OLD_CLASSIFICATION_PROMPT},
    )
    db.execute(
        sa.text("UPDATE chat_intents SET whentouse = :new "
                "WHERE name = 'booking' AND whentouse = :old"),
        {"new": NEW_BOOKING_WHENTOUSE, "old": OLD_BOOKING_WHENTOUSE},
    )


def downgrade() -> None:
    db = op.get_bind()
    db.execute(
        sa.text("UPDATE chat_intents SET whentouse = :old "
                "WHERE name = 'booking' AND whentouse = :new"),
        {"old": OLD_BOOKING_WHENTOUSE, "new": NEW_BOOKING_WHENTOUSE},
    )
    db.execute(
        sa.text("UPDATE llmsettings SET classificationprompt = :old "
                "WHERE classificationprompt IS NULL"),
        {"old": OLD_CLASSIFICATION_PROMPT},
    )
