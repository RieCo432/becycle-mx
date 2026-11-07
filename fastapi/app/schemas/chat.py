from datetime import datetime
from typing import Literal
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
    
    
    
    
class WebSocketPing(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.PING]
    
    
class WebSocketPong(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.PONG]
    
    
class WebSocketSubscribePayload(BaseModel):
    conversationIds: list[UUID]

class WebSocketSubscribe(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.SUBSCRIBE]
    payload: WebSocketSubscribePayload
    
    
    
class WebSocketChatMessagePayload(BaseModel):
    conversationId: UUID
    body: str
    
class WebSocketChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.MESSAGE]
    payload: WebSocketChatMessagePayload | MessageBase


class WebSocketErrorPayload(BaseModel):
    model_config = ConfigDict(strict=True)
    # the incoming command that was rejected
    command: Literal[WebSocketCommand.SUBSCRIBE, WebSocketCommand.MESSAGE]
    reason: str
    conversationIds: list[UUID] = []


class WebSocketError(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.ERROR]
    payload: WebSocketErrorPayload


class WebSocketConversation(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.CONVERSATION]
    payload: Conversation


# client -> server
WebSocketMessageIn = WebSocketPing | WebSocketSubscribe | WebSocketChatMessage
# client <-> server
WebSocketMessage = WebSocketMessageIn | WebSocketPong | WebSocketError | WebSocketConversation
    
    
