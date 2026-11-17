from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .appointments import Appointment
from .user import User
from .client import Client
from app.services.misc_helpers import WebSocketCommand


class UserMinimal(BaseModel):
    id: UUID
    username: str



class Participant(BaseModel):
    id: UUID
    user: UserMinimal | None = None
    client: Client | None = None


class Message(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)
    id: UUID

    conversationId: UUID
    # conversation: "Conversation"

    sentOn: datetime

    sentByParticipantId:UUID
    # Staff variant: the sender — a username for a staff/AI message, the client
    # record for the client's — so staff see who sent what in a client's chat.
    # Client variant: stays None — a customer must not receive the serving
    # volunteer's username (crud.chats.message_payload builds both variants).
    sentByParticipant: Participant | None = None

    readByParticipantId: UUID | None = None
    readOn: datetime | None = None
    # Staff variant only (None in the client variant), as above.
    readByParticipant: Participant | None = None

    body: str

    # #501 C-16: True when this message was sent by the workshop's assistant
    # (the stable ai-agent identity) — computed by the server from the sending
    # participant at serialisation time, never stored (the DB has no such
    # column, so the flag follows the identity if it ever moves). Always False
    # for human messages, in both variants. Drives the "AI" flag in the chat UI.
    agentSent: bool = False

    # #501 C-7: the intent this reply was produced for (see the model).
    intent: str | None = None


class Conversation(BaseModel):
    id: UUID
    initiatorParticipantId: UUID
    initiatorParticipant: Participant

    messages: list[Message]


class ChatIntentBase(BaseModel):
    # `name` is the classifier's slug + the dispatch key, so it must be a stable
    # token (lowercase letters, digits, underscores). The crud layer normalises
    # whatever the UI sends (spaces, capitals) into this form.
    name: str
    whenToUse: str | None = None
    replyTemplate: str
    enabled: bool = True
    orderIndex: int = 0


class ChatIntentCreate(ChatIntentBase):
    pass


class ChatIntentUpdate(BaseModel):
    # All optional: a partial patch. `name` is re-normalised like on create.
    name: str | None = None
    whenToUse: str | None = None
    replyTemplate: str | None = None
    enabled: bool | None = None
    orderIndex: int | None = None


class ChatIntent(ChatIntentBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class FragmentInfo(BaseModel):
    """A live-data fragment a reply template can reference (#501).

    `example` is computed from this shop's own data at call time; it is None when
    the shop has no data for that fragment (in which case a template referencing
    it falls through to the free-form fallback rather than sending a gap).
    """
    name: str
    description: str
    example: str | None = None
    
    
    
    
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
    # Bounded by ChatManager (CHAT_MESSAGE_MAX_LENGTH), not here: a schema
    # violation would tear down the connection, but an oversized body is a
    # rejectable message, not a protocol violation.
    body: str
    
class WebSocketChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.MESSAGE]
    payload: WebSocketChatMessagePayload | Message


class WebSocketErrorPayload(BaseModel):
    model_config = ConfigDict(strict=True)
    # the incoming command that was rejected
    # (None: the connection itself was rejected, e.g. an invalid token)
    command: Literal[WebSocketCommand.SUBSCRIBE, WebSocketCommand.MESSAGE, WebSocketCommand.MARK_READ] | None = None
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
    
    
class WebsocketMarkReadPayload(BaseModel):
    conversationId: UUID
    messageIds: list[UUID]
    participantId: UUID
    readOn: datetime
    # Staff variant: who marked it read (username/client record). Client
    # variant: None — no usernames cross to the customer (crud.chats builds
    # both variants).
    readByParticipant: Participant | None = None


class WebSocketMarkRead(BaseModel):
    model_config = ConfigDict(strict=True)
    command: Literal[WebSocketCommand.MARK_READ]
    payload: WebsocketMarkReadPayload


# client -> server
WebSocketMessageIn = WebSocketPing | WebSocketSubscribe | WebSocketChatMessage | WebSocketMarkRead
# client <-> server
WebSocketMessage = WebSocketMessageIn | WebSocketPong | WebSocketError | WebSocketConversation
    
    
