"""#500 seed the ai-agent user and participant

Revision ID: 6bce1001cca9
Revises: 2ef0b68024d6
Create Date: 2026-11-14 14:44:54

"""
from typing import Sequence, Union

import bcrypt
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bce1001cca9'
down_revision: Union[str, None] = '2ef0b68024d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The Agent sends chat messages as a stable assistant identity. A message's
    # sender is a Participant (messages.sentbyparticipantid is NOT NULL), and a
    # Participant links to a User via users.participantid. So we seed:
    #   1) a participants row  -> the assistant's sender identity
    #   2) a users row         -> the "ai-agent" account that owns it
    #
    # The "ai-agent" account is deliberately made non-interactive: its password
    # is the app's banned default, the literal string "password", which the public
    # token endpoint (/public/users/token) rejects before bcrypt with
    # "Cannot login with default password". Storing its bcrypt hash therefore
    # means the account can never be used to obtain a token, while still existing
    # as a sender. pin is left NULL so the password-or-pin paths also fail.
    participant_id = str(uuid4())
    ai_agent_password = bcrypt.hashpw(b"password", bcrypt.gensalt())
    if isinstance(ai_agent_password, bytes):
        ai_agent_password = ai_agent_password.decode()

    op.execute(
        sa.text("INSERT INTO participants (id) VALUES (:participant_id)")
        .bindparams(participant_id=participant_id)
    )
    op.execute(
        sa.text(
            "INSERT INTO users "
            "(username, password, pin, rentalchecker, softdeleted, participantid) "
            "VALUES ('ai-agent', :password, NULL, FALSE, FALSE, :participant_id)"
        ).bindparams(password=ai_agent_password, participant_id=participant_id)
    )


def downgrade() -> None:
    participant_id = op.get_bind().execute(
        sa.text("SELECT participantid FROM users WHERE username = 'ai-agent'")
    ).scalar_one_or_none()

    # Delete in FK order: messages reference the participant, the user references
    # the participant, so clear the messages, then the user, then the participant.
    if participant_id is not None:
        op.execute(
            sa.text("DELETE FROM messages WHERE sentbyparticipantid = :participant_id")
            .bindparams(participant_id=participant_id)
        )

    op.execute(sa.text("DELETE FROM users WHERE username = 'ai-agent'"))

    if participant_id is not None:
        op.execute(
            sa.text("DELETE FROM participants WHERE id = :participant_id")
            .bindparams(participant_id=participant_id)
        )
