import asyncio
import time
from asyncio import sleep
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4, UUID

from pydantic import TypeAdapter
from sqlalchemy import select

from fastapi import WebSocket
from starlette.exceptions import WebSocketException
from starlette.websockets import WebSocketDisconnect, WebSocketState, WebSocket

import app.models as models
import app.schemas as schemas
import os

import sqlalchemy.exc
from fastapi import HTTPException, status

from jose import jwt, JWTError
from sqlalchemy.orm import Session


from app.database.db import SessionLocal
from app.services.misc_helpers import WebSocketCommand

from .permissions import check_permission, get_permission_by_route_and_method

API_SECRET = os.environ['API_SECRET']
API_SECRET_ALGORITHM = os.environ['API_SECRET_ALGORITHM']
PRODUCTION = os.environ['PRODUCTION'] == "true"

# How long to wait for the client's token frame before giving up. A client
# that accepts the connection and then sends nothing must not be able to
# park a server task (and an open connection) forever.
WS_HANDSHAKE_TIMEOUT = 10
# 4xxx close codes are reserved for application use. The frontend treats
# this as terminal: the token is bad, so retrying with the same token cannot
# succeed.
WS_CLOSE_AUTH_FAILED = 4401

# A human can't type this fast: more messages than this from a single socket
# within this window is a client bug or abuse, not typing.
MSG_RATE_LIMIT = 5        # messages per socket within the window
MSG_RATE_WINDOW = 5.0     # seconds
CHAT_MESSAGE_MAX_LENGTH = 2000  # characters


def get_or_create_participant(db: Session, entity: models.User | models.Client) -> models.Participant:
    participant = db.scalar(
        select(models.Participant)
        .where(models.Participant.id == entity.participantId)
    )

    if participant is None:
        participant = models.Participant()
        db.add(participant)
        db.commit()
        db.refresh(participant)

        entity.participantId = participant.id
        db.commit()

    return participant


def get_or_create_conversation(db: Session, participant: models.Participant) -> tuple[models.Conversation, bool]:
    conversation = db.scalar(
        select(models.Conversation)
        .where(models.Conversation.initiatorParticipantId == participant.id)
    )
    if conversation is not None:
        return conversation, False

    conversation = models.Conversation(
        initiatorParticipantId=participant.id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation, True


def get_participant_by_id(db: Session, participant_id: UUID) -> models.Participant | None:
    participant = db.scalar(
        select(models.Participant)
        .where(models.Participant.id == participant_id)
    )

    return participant


def get_conversations(db: Session) -> list[schemas.Conversation]:
    all_conversations = db.scalars(
        select(models.Conversation)
    )
    
    client_conversations = []
    for conversation in all_conversations:
        if conversation.initiatorParticipant.client is not None:
            client_conversations.append(conversation)

    return client_conversations


def get_participant_by_token(db: Session, token: str) -> models.Participant | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"description": "Could not validate credentials. Please login again."},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, API_SECRET, algorithms=[API_SECRET_ALGORITHM])
        participant_id: str = payload.get("participant_id")
        if participant_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    participant = get_participant_by_id(db=db, participant_id=UUID(participant_id))
    if participant is None:
        raise credentials_exception
    return participant


async def send_websocket_message(socket: WebSocket, message: schemas.WebSocketMessage):
    await socket.send_json(message.model_dump(mode="json"))


async def close_websocket(websocket: WebSocket, code: int = 1000) -> None:
    """Close the socket, tolerating a peer that already went away (a close
    on a half-dead connection can itself raise) — by the time we are
    closing because of a failure, the close is best-effort bookkeeping."""
    try:
        await websocket.close(code=code)
    except Exception as e:
        print(f"failed to close socket: {e}")


async def send_unauthorized_frame(websocket: WebSocket) -> None:
    """Best-effort 'here is why this connection is dying' frame, sent before
    the auth-failure close so the client can surface a real message instead
    of flapping. A peer that is already gone simply gets no frame — that
    must not mask the original failure."""
    if websocket.state != WebSocketState.CONNECTED:
        return
    try:
        await send_websocket_message(
            websocket,
            schemas.WebSocketError(
                command=schemas.WebSocketCommand.ERROR,
                payload=schemas.WebSocketErrorPayload(
                    command=None,
                    reason="unauthorized",
                ),
            ),
        )
    except Exception:
        pass


# Only accept the client -> server commands; pong/error are server -> client.
websocket_message_adapter = TypeAdapter(schemas.WebSocketMessageIn)


def participant_may_see_conversations(db: Session, participant_id: UUID) -> bool:
    """Whether a participant may see the conversation list at all: staff
    users holding the ``GET /chats/conversations`` permission (the same
    gate as the list route)."""
    user = db.scalar(
        select(models.User)
        .where(models.User.participantId == participant_id)
    )
    if user is None:
        return False

    permission = get_permission_by_route_and_method(db=db, route="/chats/conversations", method="GET")
    return permission is not None and check_permission(db=db, user=user, permission=permission)


def participant_can_access_conversation(db: Session, participant_id: UUID, conversation_id: UUID) -> bool:
    """A participant may use a conversation over the websocket if they could
    read it via REST: a client may use their own conversation, and a staff
    user may use every conversation when they may see the conversation
    list (see ``participant_may_see_conversations``)."""
    conversation = db.scalar(
        select(models.Conversation)
        .where(models.Conversation.id == conversation_id)
    )
    if conversation is None:
        return False

    if conversation.initiatorParticipantId == participant_id:
        return True

    return participant_may_see_conversations(db=db, participant_id=participant_id)


def get_message(db: Session, conversation_id: UUID, message_id: UUID) -> models.Message | None:
    """Get a message by conversation and message ID."""
    return db.scalar(
        select(models.Message)
        .where(models.Message.conversationId == conversation_id)
        .where(models.Message.id == message_id)
    )


@asynccontextmanager
async def session_scope():
    # One fresh session per websocket operation: sessions are not safe to
    # share across concurrent sockets, and closing in `finally` guarantees
    # the connection is released even if the operation raises.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.participant_sockets: dict[UUID, list[UUID]] = {}
        self.subscriptions: dict[UUID, set[UUID]] = {}
        self.ping_times: dict[UUID, datetime] = {}
        # socket_id -> monotonic timestamps of its recent message frames (rate limit)
        self.message_times: dict[UUID, deque[float]] = {}
        self.ping_loop = asyncio.create_task(self.keep_tabs())
        
    async def keep_tabs(self):
        while True:
            if not PRODUCTION:
                print("checking ping times")
            now = datetime.now(timezone.utc)
            for participant_id, socket_ids in list(self.participant_sockets.items()):
                for socket_id in list(socket_ids):
                    try:
                        last_ping = self.ping_times.get(socket_id)
                        if last_ping is not None and (now - last_ping).total_seconds() > 60:
                            if not PRODUCTION:
                                print("no ping received in 60 seconds")
                            await self.disconnect(socket_id, participant_id)
                    except Exception as e:
                        print(f"keep_tabs: failed to disconnect stale socket {socket_id}: {e}")
            await sleep(30)
        


    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        try:
            token_message = await asyncio.wait_for(
                websocket.receive_json(), timeout=WS_HANDSHAKE_TIMEOUT
            )
        except WebSocketDisconnect:
            # The client went away before sending the token — nothing to do.
            raise
        except Exception:
            # No token in time, or an unreadable first frame: tell the client
            # (if it is still there) and close — an accepted-but-never-serviced
            # connection must not be left open.
            await send_unauthorized_frame(websocket)
            await close_websocket(websocket, code=WS_CLOSE_AUTH_FAILED)
            raise

        try:
            async with session_scope() as db:
                participant = get_participant_by_token(token=token_message["token"], db=db)
        except WebSocketDisconnect:
            raise
        except Exception:
            # Bad/expired/unknown token. Tell the client why and close with
            # the terminal auth-failure code, so it stops retrying the same
            # token. Re-raise so the endpoint can log and clean up.
            await send_unauthorized_frame(websocket)
            await close_websocket(websocket, code=WS_CLOSE_AUTH_FAILED)
            raise
        if participant is None:
            raise WebSocketException
        if participant.id not in self.participant_sockets:
            self.participant_sockets[participant.id] = []
            
        socket_id = uuid4()
        self.active_connections[socket_id] = websocket
        self.ping_times[socket_id] = datetime.now(timezone.utc)
        self.participant_sockets[participant.id].append(socket_id)
        
        print("Active connections:", len(self.active_connections))
        return socket_id, participant
    
    def subscribe(self, conversation_id: UUID, participant_id: UUID):
        if conversation_id not in self.subscriptions:
            self.subscriptions[conversation_id] = set()
        self.subscriptions[conversation_id].add(participant_id)

    def message_allowed(self, socket_id: UUID) -> bool:
        """Per-socket sliding-window rate limit for message frames. Only
        accepted frames are recorded, so a flood of rejects cannot extend its
        own lockout."""
        now = time.monotonic()
        times = self.message_times.setdefault(socket_id, deque())
        while times and now - times[0] > MSG_RATE_WINDOW:
            times.popleft()
        if len(times) >= MSG_RATE_LIMIT:
            return False
        times.append(now)
        return True
        
    async def broadcast(self, websocket_message: schemas.WebSocketChatMessage | schemas.WebSocketMarkRead):
        # Nobody may be subscribed to this conversation (subscriptions are
        # only requested once, at connect time) — nothing to deliver.
        participant_ids = self.subscriptions.get(websocket_message.payload.conversationId)
        if not participant_ids:
            return

        # Snapshot both levels: another socket's task may run while we await
        # a send and change either collection (e.g. a disconnect).
        for participant_id in list(participant_ids):
            for websocket_id in list(self.participant_sockets.get(participant_id, ())):
                websocket = self.active_connections.get(websocket_id)
                if websocket is None:
                    continue
                try:
                    await send_websocket_message(websocket, websocket_message)
                except Exception as e:
                    # One dead recipient must not stop delivery to the rest,
                    # or tear down the sender's connection.
                    print(f"failed to deliver message to socket {websocket_id}: {e}")

    async def notify_new_conversation(self, conversation: schemas.Conversation):
        """Push a freshly-created conversation to every connected participant
        who may see the conversation list (staff with the matching
        permission). Mirrors the list route: only client-initiated
        conversations are pushed. Clients never receive this — they only
        ever see their own conversation, which their REST response already
        contains."""
        if conversation.initiatorParticipant.client is None:
            return

        frame = schemas.WebSocketConversation(
            command=schemas.WebSocketCommand.CONVERSATION,
            payload=conversation,
        )
        for participant_id in list(self.participant_sockets.keys()):
            async with session_scope() as db:
                if not participant_may_see_conversations(db=db, participant_id=participant_id):
                    continue
            for websocket_id in list(self.participant_sockets.get(participant_id, ())):
                websocket = self.active_connections.get(websocket_id)
                if websocket is None:
                    continue
                try:
                    await send_websocket_message(websocket, frame)
                except Exception as e:
                    # One dead recipient must not stop the others.
                    print(f"failed to notify socket {websocket_id} about conversation {conversation.id}: {e}")

    async def disconnect(self, socket_id: UUID, participant_id: UUID):
        websocket = self.active_connections.pop(socket_id, None)
        if websocket is not None and websocket.state == WebSocketState.CONNECTED:
            if not PRODUCTION:
                print("Closing connection for participant:", participant_id)
            try:
                await websocket.close()
            except Exception as e:
                print(f"Failed to close socket {socket_id}: {e}")

        socket_ids = self.participant_sockets.get(participant_id)
        if socket_ids is not None and socket_id in socket_ids:
            socket_ids.remove(socket_id)
            if not socket_ids:
                del self.participant_sockets[participant_id]
                # The participant is fully gone: drop their subscriptions so
                # they don't accumulate forever. They re-subscribe on
                # reconnect (the client sends subscribe after every connect).
                for conversation_id, participants in self.subscriptions.items():
                    participants.discard(participant_id)
                for conversation_id in [cid for cid, p in self.subscriptions.items() if not p]:
                    del self.subscriptions[conversation_id]

        self.ping_times.pop(socket_id, None)
        self.message_times.pop(socket_id, None)
        print("Active connections:", len(self.active_connections))
        
    async def take_it_from_here(self, socket_id: UUID, participant: models.Participant):
        socket = self.active_connections[socket_id]
        while True:
            try:
                request_json = await socket.receive_text()  
                request: schemas.WebSocketMessage = websocket_message_adapter.validate_json(request_json)
                
                if isinstance(request, schemas.WebSocketSubscribe):
                    rejected = []
                    async with session_scope() as db:
                        for conversation_id in request.payload.conversationIds:
                            if participant_can_access_conversation(
                                db=db, participant_id=participant.id, conversation_id=conversation_id
                            ):
                                self.subscribe(conversation_id=conversation_id, participant_id=participant.id)
                            else:
                                rejected.append(conversation_id)

                    if rejected:
                        print(f"denied: participant {participant.id} may not use conversations: {rejected}")
                        await send_websocket_message(
                            socket,
                            schemas.WebSocketError(
                                command=schemas.WebSocketCommand.ERROR,
                                payload=schemas.WebSocketErrorPayload(
                                    command=schemas.WebSocketCommand.SUBSCRIBE,
                                    reason="forbidden",
                                    conversationIds=rejected,
                                ),
                            ),
                        )

                elif isinstance(request, schemas.WebSocketChatMessage):
                    conversation_id = request.payload.conversationId
                    # In-memory hardening first: a flood or an oversized body
                    # is rejected without ever touching the database. Every
                    # message frame consumes rate budget — including ones we
                    # are about to reject for size — so a flood of junk cannot
                    # bypass the limit.
                    if not self.message_allowed(socket_id):
                        print(f"denied: message rate limit exceeded for socket {socket_id}")
                        await send_websocket_message(
                            socket,
                            schemas.WebSocketError(
                                command=schemas.WebSocketCommand.ERROR,
                                payload=schemas.WebSocketErrorPayload(
                                    command=schemas.WebSocketCommand.MESSAGE,
                                    reason="rate_limited",
                                    conversationIds=[conversation_id],
                                ),
                            ),
                        )
                        continue

                    if len(request.payload.body) > CHAT_MESSAGE_MAX_LENGTH:
                        print(f"denied: body of {len(request.payload.body)} chars exceeds {CHAT_MESSAGE_MAX_LENGTH} (socket {socket_id})")
                        await send_websocket_message(
                            socket,
                            schemas.WebSocketError(
                                command=schemas.WebSocketCommand.ERROR,
                                payload=schemas.WebSocketErrorPayload(
                                    command=schemas.WebSocketCommand.MESSAGE,
                                    reason="too_long",
                                    conversationIds=[conversation_id],
                                ),
                            ),
                        )
                        continue

                    async with session_scope() as db:
                        if not participant_can_access_conversation(
                            db=db, participant_id=participant.id, conversation_id=conversation_id
                        ):
                            print(f"denied: participant {participant.id} may not message conversation {conversation_id}")
                            await send_websocket_message(
                                socket,
                                schemas.WebSocketError(
                                    command=schemas.WebSocketCommand.ERROR,
                                    payload=schemas.WebSocketErrorPayload(
                                        command=schemas.WebSocketCommand.MESSAGE,
                                        reason="forbidden",
                                        conversationIds=[conversation_id],
                                    ),
                                ),
                            )
                            continue

                        message = models.Message(
                            conversationId=conversation_id,
                            sentByParticipantId=participant.id,
                            body=request.payload.body)
                        db.add(message)
                        db.commit()
                        db.refresh(message)

                        websocket_message = schemas.WebSocketChatMessage(
                            command=schemas.WebSocketCommand.MESSAGE,
                            payload=schemas.Message.model_validate(message, from_attributes=True)
                        )
                    # The session is closed before the broadcast on purpose:
                    # no DB connection is held open while sending to sockets.
                    
                    await self.broadcast(websocket_message)
                    
                elif isinstance(request, schemas.WebSocketPing):
                    if not PRODUCTION:
                        print(socket_id, "ping")
                    self.ping_times[socket_id] = datetime.now(timezone.utc)
                    await send_websocket_message(socket, schemas.WebSocketPong(command=schemas.WebSocketCommand.PONG))
                    
                elif isinstance(request, schemas.WebSocketMarkRead):
                    conversation_id = request.payload.conversationId
                    if not PRODUCTION:
                        print(socket_id, "mark_read")

                    async with session_scope() as db:
                        if not participant_can_access_conversation(
                                db=db, participant_id=participant.id, conversation_id=conversation_id
                        ):
                            print(f"denied: participant {participant.id} may not message conversation {conversation_id}")
                            await send_websocket_message(
                                socket,
                                schemas.WebSocketError(
                                    command=schemas.WebSocketCommand.ERROR,
                                    payload=schemas.WebSocketErrorPayload(
                                        command=schemas.WebSocketCommand.MARK_READ,
                                        reason="forbidden",
                                        conversationIds=[conversation_id],
                                    ),
                                ),
                            )
                            continue
    
                        for messageId in request.payload.messageIds:
                            message = get_message(db=db, conversation_id=conversation_id, message_id=messageId)
                            if message is not None:
                                message.readByParticipantId = participant.id
                                message.readOn = request.payload.readOn
                                db.commit()
                        
                        request.payload.readByParticipant = participant
                        
                        websocket_message = schemas.WebSocketMarkRead(
                            command=schemas.WebSocketCommand.MARK_READ,
                            payload=schemas.WebsocketMarkReadPayload.model_validate(request.payload, from_attributes=True)
                        )

                    # The session is closed before the broadcast on purpose:
                    # no DB connection is held open while sending to sockets.
    
                    await self.broadcast(websocket_message)
                
                
            except Exception as e:
                print(e)
                await self.disconnect(socket_id, participant.id)
                break
        
    