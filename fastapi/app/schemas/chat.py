from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .appointments import Appointment
from .user import User
from .client import Client
from app.services.misc_helpers import WebSocketCommand

class Participant(BaseModel):
    id: UUID
    user: User | None = None
    client: Client | None = None


class MessageBase(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)
    id: UUID

    conversationId: UUID
    # conversation: "Conversation"

    sentOn: datetime

    sentByParticipantId:UUID

    seenByParticipantId: UUID | None = None

    body: str


class MessageFull(MessageBase):
    model_config = ConfigDict(strict=True, from_attributes=True)
    sentByParticipant: Participant
    seenByParticipant: Participant | None = None
    
    
class Conversation(BaseModel):
    id: UUID
    initiatorParticipantId: UUID
    initiatorParticipant: Participant
    
    messages: list[MessageFull]
    
    
    
class WebSocketSubscribe(BaseModel):
    conversationIds: list[UUID]
    
    
class WebSocketMessage(BaseModel):
    conversationId: UUID
    body: str
    
    
class WebSocketRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    command: WebSocketCommand
    payload: WebSocketSubscribe | WebSocketMessage
    
    
