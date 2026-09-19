from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .appointments import Appointment
from .user import User
from .client import Client

class Participant(BaseModel):
    id: UUID
    user: User | None = None
    client: Client | None = None


class MessageBase(BaseModel):
    id: UUID

    conversationId: UUID
    # conversation: "Conversation"

    sentOn: datetime

    sentByParticipantId:UUID

    seenByParticipantId: UUID | None = None

    body: str


class MessageFull(MessageBase):
    sentByParticipant: Participant
    seenByParticipant: Participant | None = None
    
    
class Conversation(BaseModel):
    id: UUID
    initiatorParticipantId: UUID
    initiatorParticipant: Participant
    
    messages: list[MessageFull]
    
    
