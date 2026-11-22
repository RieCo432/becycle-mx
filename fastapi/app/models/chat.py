from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import UUID, text, Text, DateTime, ForeignKey, String, Boolean, Integer, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.extensions.chatactionflowtype import ChatActionFlowType
from app.extensions.chatactionflowstage import ChatActionFlowStage

from typing import List

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    conversationId: Mapped[UUID] = mapped_column("conversationid", ForeignKey("conversations.id"), nullable=False, quote=False)
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    sentOn: Mapped[datetime] = mapped_column("senton", DateTime, nullable=False, default=lambda _: datetime.now(timezone.utc), server_default=text("(current_timestamp at time zone 'utc')"), quote=False, index=True)

    sentByParticipantId: Mapped[UUID] = mapped_column("sentbyparticipantid", ForeignKey("participants.id"), nullable=False, quote=False)
    sentByParticipant: Mapped["Participant"] = relationship("Participant", foreign_keys=[sentByParticipantId], back_populates="messagesSent")
    
    readOn: Mapped[datetime | None] = mapped_column("seenon", DateTime, nullable=True, quote=False, index=True)

    readByParticipantId: Mapped[UUID] = mapped_column("readbyparticipantid", ForeignKey("participants.id"), nullable=True, quote=False)
    readByParticipant: Mapped["Participant"] = relationship("Participant", foreign_keys=[readByParticipantId], back_populates="messagesRead")

    body: Mapped[str] = mapped_column("body", Text, nullable=False, quote=False)

    # #501 C-7: the intent a client auto-reply was produced for (e.g. "hours",
    # "open_today"), or the "none" sentinel when it came from the free-form
    # fallback. Stored as a plain label (no FK): an intent can be added, renamed,
    # or removed later without breaking replies that already recorded it.
    intent: Mapped[str | None] = mapped_column("intent", String(64), nullable=True, quote=False)

    # #510 A-8: the staff quality rating of an AI reply, set in the audit
    # trail: true = good, false = not good, null = not yet rated.
    qualityRating: Mapped[bool | None] = mapped_column("qualityrating", Boolean, nullable=True, quote=False)


class ChatIntent(Base):
    """A client-chat intent (#501): a classified route the Agent dispatches to.

    The set is editable per org — each shop's own database holds its rows — via the
    LLM settings UI. `name` is the stable slug the classifier emits and the
    dispatcher matches on; `whenToUse` feeds the classification prompt;
    `replyTemplate` is the pre-formed reply, which may reference live-data
    fragments ({{name}}) that the handler assembles from the shop's own data
    (C-5: LLM-independent).
    """
    __tablename__ = "chat_intents"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    name: Mapped[str] = mapped_column("name", String(64), nullable=False, unique=True, index=True, quote=False)
    whenToUse: Mapped[str | None] = mapped_column("whentouse", Text, nullable=True, quote=False)
    replyTemplate: Mapped[str] = mapped_column("replytemplate", Text, nullable=False, quote=False)
    enabled: Mapped[bool] = mapped_column("enabled", Boolean, nullable=False, default=True, server_default=text("TRUE"), quote=False)
    orderIndex: Mapped[int] = mapped_column("orderindex", Integer, nullable=False, default=0, server_default=text("0"), quote=False)


class Participant(Base):
    __tablename__ = "participants"
    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    
    user: Mapped["User | None"] = relationship("User", back_populates="participant")
    client: Mapped["Client | None"] = relationship("Client", back_populates="participant")
    
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="initiatorParticipant")
    messagesSent: Mapped[List["Message"]] = relationship("Message", foreign_keys=[Message.sentByParticipantId], back_populates="sentByParticipant")
    messagesRead: Mapped[List["Message"]] = relationship("Message", foreign_keys=[Message.readByParticipantId], back_populates="readByParticipant")
    

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    initiatorParticipantId: Mapped[UUID] = mapped_column("initiatorparticipantid", ForeignKey("participants.id"), nullable=False, quote=False, unique=True)
    initiatorParticipant: Mapped[Participant] = relationship("Participant", back_populates="conversation")

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation")

    flows: Mapped[List["ChatActionFlow"]] = relationship("ChatActionFlow", back_populates="conversation")


class ChatActionFlow(Base):
    """One in-progress chat action flow — generic across flow types (#503).

    Future chat-based action flows (a lending flow, a parts order, ...) reuse
    this table rather than adding one per flow: `flowtype` says which handler
    owns the row, and the flow's own state lives in the JSON `data` payload,
    validated by that flow's crud (for 'booking': appointmentTypeId,
    pendingSlot, offeredSlots, reoffersUsed — see the BookingFlowData shape there).

    #503 B-9: this is the one stateful route — unlike the stateless #500 / #501
    handlers, the flow remembers where it is across debounced bursts, so it can
    resume mid-flow.

    Ephemeral by design: at most one active flow of each type per conversation
    (the unique conversationid+flowtype means "a flow of that type is in
    progress"), and a terminal outcome — booked, handed off, turn budget
    exhausted — deletes the row, so the next flow starts fresh. The audit trail
    of what actually happened is the assistant's replies themselves (messages
    with intent 'booking', #510).
    """
    __tablename__ = "chatactionflows"
    __table_args__ = (
        # One active flow of each type per conversation: a 'booking' flow and a
        # future 'lending' flow may coexist, but a second of the same type
        # cannot (a burst must never branch into two of the same flow).
        UniqueConstraint("conversationid", "flowtype", name="uq_chatactionflows_conversationid_flowtype"),
    )

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    conversationId: Mapped[UUID] = mapped_column("conversationid", ForeignKey("conversations.id"), nullable=False, quote=False)
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="flows")

    # Which handler owns this row (extensions/chatactionflowtype.py): 'booking'
    # for the #503 booking flow. A future action flow adds its value in its own
    # migration rather than adding a table.
    flowtype: Mapped[ChatActionFlowType] = mapped_column("flowtype", Enum(ChatActionFlowType, native_enum=True), nullable=False, quote=False)

    # Where the flow is (extensions/chatactionflowstage.py), namespaced per
    # flow type (BOOKING_*) so the shared column can't hold a stage that is
    # not in its flow type's vocabulary.
    stage: Mapped[ChatActionFlowStage] = mapped_column("stage", Enum(ChatActionFlowStage, native_enum=True), nullable=False, quote=False)

    # The flow's own payload (see the class docstring for the booking shape).
    data: Mapped[dict] = mapped_column("data", JSON, nullable=False, server_default=text("'{}'"), quote=False)

    # The flow's turn budget counter (a turn is one assistant message in the
    # flow). The budget itself is per flow type — 6 for booking, enforced by
    # the flow crud.
    turnsUsed: Mapped[int] = mapped_column("turnsused", Integer, nullable=False, default=0, server_default=text("0"), quote=False)

    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=lambda _: datetime.now(timezone.utc), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)


# conversation_participants_association_table = Table(
#     "conversationparticipants",
#     Base.metadata,
#     Column("id")
#     Column("conversationid", ForeignKey("conversations.id"), primary_key=True),
#     Column("participantid", ForeignKey("participants.id"), primary_key=True),
#     Column("joinedon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False, index=True),
#     Column("lefton", DateTime, nullable=True, quote=False, index=True),
# )



