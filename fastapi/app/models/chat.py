from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, text, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

from typing import List

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    conversationId: Mapped[UUID] = mapped_column("conversationid", ForeignKey("conversations.id"), nullable=False, quote=False)
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    sentOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False, index=True)

    sentByParticipantId: Mapped[UUID] = mapped_column("sentbyparticipantid", ForeignKey("participants.id"), nullable=False, quote=False)
    sentByParticipant: Mapped["Participant"] = relationship("Participant", foreign_keys=[sentByParticipantId], back_populates="messagesSent")

    seenByParticipantId: Mapped[UUID] = mapped_column("seenbyparticipantid", ForeignKey("participants.id"), nullable=True, quote=False)
    seenByParticipant: Mapped["Participant"] = relationship("Participant", foreign_keys=[seenByParticipantId], back_populates="messagesSeen")

    body: Mapped[str] = mapped_column("body", Text, nullable=False, quote=False)
    
    
class Participant(Base):
    __tablename__ = "participants"
    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    
    user: Mapped["User | None"] = relationship("User", back_populates="participant")
    client: Mapped["Client | None"] = relationship("Client", back_populates="participant")
    
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="initiatorParticipant")
    messagesSent: Mapped[List["Message"]] = relationship("Message", foreign_keys=[Message.sentByParticipantId], back_populates="sentByParticipant")
    messagesSeen: Mapped[List["Message"]] = relationship("Message", foreign_keys=[Message.seenByParticipantId], back_populates="seenByParticipant")
    

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



