from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import UUID, text, Text, DateTime, ForeignKey, String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

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


# conversation_participants_association_table = Table(
#     "conversationparticipants",
#     Base.metadata,
#     Column("id")
#     Column("conversationid", ForeignKey("conversations.id"), primary_key=True),
#     Column("participantid", ForeignKey("participants.id"), primary_key=True),
#     Column("joinedon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False, index=True),
#     Column("lefton", DateTime, nullable=True, quote=False, index=True),
# )



