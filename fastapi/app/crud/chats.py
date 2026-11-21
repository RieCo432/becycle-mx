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
from app.services.llm_agent import converse, classify, NONE_INTENT
from app.services.misc_helpers import WebSocketCommand

from .permissions import check_permission, get_permission_by_route_and_method
from .settings import get_llm_settings
from .intents import get_intent_by_name, evaluate_template, get_faq_answer_by_key
from .users import get_user_by_username

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

# The stable assistant identity (#500 AS-4): the Agent always sends as this
# user. Single source of truth for both looking it up (agent flush) and
# recognising its messages (message_payload's agentSent flag).
AI_AGENT_USERNAME = "ai-agent"


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
            # Staff-only list: the full variant (staff see who sent what).
            client_conversations.append(
                conversation_payload(conversation, include_participants=True)
            )

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


def message_payload(message: models.Message, *, include_participants: bool = False) -> schemas.Message:
    """Serialise one message for the wire (REST history + WS frames).

    Two variants, chosen by who receives it:
    - `include_participants=True` (staff variant): the nested sender is
      included — a username for a staff/AI message, the client record for the
      client's — so staff see who sent what in a client's chat.
    - `include_participants=False` (client variant): the nested objects stay
      None — a customer must not receive the serving volunteer's username;
      the opaque participant IDs stay (own-side detection in the UI).

    `agentSent` is computed from the sending participant — the stable
    assistant identity (ai-agent) — in both variants, and never stored: the
    DB has no such column, so the flag follows the identity if it ever moves.

    The single place that decides what a message looks like to a client, so
    the rules can't drift between the send paths. Call with the session open
    (the participant relationships are lazy-loaded).
    """
    sender = message.sentByParticipant
    reader = message.readByParticipant if include_participants else None
    return schemas.Message(
        id=message.id,
        conversationId=message.conversationId,
        sentOn=message.sentOn,
        sentByParticipantId=message.sentByParticipantId,
        sentByParticipant=(
            schemas.Participant.model_validate(sender, from_attributes=True)
            if include_participants else None
        ),
        readByParticipantId=message.readByParticipantId,
        readOn=message.readOn,
        readByParticipant=(
            schemas.Participant.model_validate(reader, from_attributes=True)
            if reader is not None else None
        ),
        body=message.body,
        agentSent=bool(
            sender is not None
            and sender.user is not None
            and sender.user.username == AI_AGENT_USERNAME
        ),
        # Staff variant only: the classification must not leak to the client
        # side of the wire (#510 A-5), like the participant objects above.
        intent=message.intent if include_participants else None,
    )


def conversation_payload(
    conversation: models.Conversation, *, include_participants: bool = False
) -> schemas.Conversation:
    """Serialise a conversation for the wire: the initiator (staff need the
    client's name; a client only ever sees their own record) plus the messages
    via message_payload. Call with the session open."""
    return schemas.Conversation(
        id=conversation.id,
        initiatorParticipantId=conversation.initiatorParticipantId,
        initiatorParticipant=schemas.Participant.model_validate(
            conversation.initiatorParticipant, from_attributes=True
        ),
        messages=[
            message_payload(m, include_participants=include_participants)
            for m in conversation.messages
        ],
    )


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


def conversation_is_owned_by(db: Session, conversation_id: UUID, participant_id: UUID) -> bool:
    """Whether ``participant_id`` is the conversation's owner (initiator) — the
    chat's client, as opposed to the staff user serving it. The agent harness
    reacts only to the owner's messages; staff messages are ordinary human chat."""
    conversation = db.scalar(
        select(models.Conversation).where(models.Conversation.id == conversation_id)
    )
    return conversation is not None and conversation.initiatorParticipantId == participant_id


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


class _DebounceBuffer:
    """Accumulate a chat owner's message bursts, per conversation, and fire a
    callback once a burst is "done" — either the silence window elapses or the
    batch cap is reached, whichever first.

    This is the harness core for #500 (H-1, H-6). It is deliberately role-agnostic:
    it only accumulates and fires; the flushed handler decides what to do with the
    batch (converse for a volunteer, classify for a client in #501). The harness
    only ever buffers the conversation's owner's messages, so the conversation id
    alone is a sufficient key — the owner is resolved from the conversation when
    the handler needs it. It owns no database, agent, or websocket state — just
    in-memory timing on the caller's event loop.

    Best-effort by contract: the flushed handler is scheduled fire-and-forget and
    its exceptions are swallowed, so the buffer can never raise into the chat path.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, on_flush):
        # on_flush: async (conversation_id, batch: list[tuple[UUID, str]]) -> None
        # Each batch entry is (message_id, body): the body is what the agent sees,
        # the id lets the handler act on exactly these messages (e.g. mark them
        # read, V-6) instead of re-deriving them.
        # The silence window and batch cap are supplied per submit() so admin edits
        # to LlmSettings apply live (no restart).
        self._loop = loop
        self._on_flush = on_flush
        self._buffers: dict[UUID, list[tuple[UUID, str]]] = {}
        self._timers: dict[UUID, asyncio.TimerHandle] = {}

    def submit(self, conversation_id: UUID, message_id: UUID, body: str, window_s: float, cap: int) -> None:
        key = conversation_id
        buffer = self._buffers.setdefault(key, [])
        buffer.append((message_id, body))
        if len(buffer) >= cap:
            # Cap reached: fire now rather than wait out the silence window.
            self._fire(key)
        else:
            # Debounce: (re)start the silence window from this message.
            self._reset_timer(key, window_s)

    def _reset_timer(self, key, window_s: float) -> None:
        existing = self._timers.get(key)
        if existing is not None:
            existing.cancel()
        self._timers[key] = self._loop.call_later(window_s, self._on_timer, key)

    def _on_timer(self, key) -> None:
        self._timers.pop(key, None)
        self._fire(key)

    def _fire(self, key) -> None:
        # Synchronous and atomic with respect to the event loop (no awaits), so a
        # burst is flushed exactly once even if submit() and the timer interleave.
        buffer = self._buffers.pop(key, None)
        timer = self._timers.pop(key, None)
        if timer is not None:
            timer.cancel()
        if not buffer:
            return
        task = self._loop.create_task(
            self._safe_flush(key, list(buffer)))
        # Reap so a failure never surfaces as "Task exception was never retrieved"
        # and never propagates into the loop.
        task.add_done_callback(self._reap)

    async def _safe_flush(self, conversation_id: UUID, batch: list[tuple[UUID, str]]) -> None:
        try:
            await self._on_flush(conversation_id, batch)
        except Exception as e:  # best-effort: a handler failure means "nothing happens"
            if not PRODUCTION:
                print(f"agent on_flush raised (ignored): {e!r}")

    @staticmethod
    def _reap(task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            return
        if exc is not None and not PRODUCTION:
            print(f"agent flush task raised (ignored): {exc!r}")


async def resolve_reply(db: Session, intent: str, messages: list[str]) -> str | None:
    """#501: turn a classified client intent into a reply (or None -> no reply).

    A configured intent assembles its stored template from live per-org data
    (C-2/C-4/C-5). A classified FAQ replies with its stored answer (deterministic,
    editable in the existing FAQ UI). If neither yields a reply — a fragment has no
    data, or the intent has no row / is disabled — fall through to the
    customerFreeForm free-form fallback (C-6). `none` goes straight to the
    fallback. Returns None when nothing should be said (C-8). The classified
    ``intent`` is what the caller records on the reply (C-7), whatever path
    produced the text.
    """
    if intent != NONE_INTENT:
        row = get_intent_by_name(db=db, name=intent)
        if row is not None and row.enabled:
            reply = evaluate_template(db=db, template=row.replyTemplate)
            if reply is not None:
                return reply
            # A referenced fragment had no data -> fall through (the no-data rule).
        faq_answer = get_faq_answer_by_key(db=db, key=intent)
        if faq_answer:
            return faq_answer
    return await _free_form_fallback(db=db, messages=messages)


async def _free_form_fallback(db: Session, messages: list[str]) -> str | None:
    """C-6: the customerFreeForm gate for unclassified / unhandled client bursts.

    Off (or unset) -> do nothing; on -> a free-form reply via the Agent.
    """
    settings = get_llm_settings(db=db)
    if settings is None or not settings.customerFreeForm:
        return None
    return await converse(db=db, messages=messages)


class ChatManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.participant_sockets: dict[UUID, list[UUID]] = {}
        self.subscriptions: dict[UUID, set[UUID]] = {}
        self.ping_times: dict[UUID, datetime] = {}
        # socket_id -> monotonic timestamps of its recent message frames (rate limit)
        self.message_times: dict[UUID, deque[float]] = {}
        self.ping_loop = asyncio.create_task(self.keep_tabs())

        # Agent harness (#500): debounce each sender's burst before firing the
        # agent. Built on this manager's event loop; best-effort, never raises.
        # The window/cap come from LlmSettings, read per message in take_it_from_here.
        self.agent_buffer = _DebounceBuffer(
            loop=asyncio.get_running_loop(),
            on_flush=self._on_agent_flush,
        )
        
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
        
    def _recipient_frames(
        self, db: Session, conversation_id: UUID,
        staff_frames: list[schemas.WebSocketMessage],
        client_frames: list[schemas.WebSocketMessage],
    ) -> dict[UUID, list[schemas.WebSocketMessage]]:
        """Map each subscribed recipient to its frame variant: staff get the
        full variant (sender identity included), clients the stripped variant
        (no volunteer usernames). The recipient kinds are read while the
        session is open; the broadcast itself happens after it closes.
        """
        subscribed = self.subscriptions.get(conversation_id)
        if not subscribed:
            return {}
        rows = db.scalars(
            select(models.Participant).where(models.Participant.id.in_(set(subscribed)))
        ).all()
        client_ids = {p.id for p in rows if p.client is not None}
        return {
            pid: (client_frames if pid in client_ids else staff_frames)
            for pid in subscribed
        }

    async def broadcast(self, conversation_id: UUID, frames: dict[UUID, list[schemas.WebSocketMessage]]):
        """Deliver per-recipient frame sets to a conversation's subscribers.

        `frames` maps participant_id → the ordered frames for that participant
        (the staff/client variants, built while the session was open — a
        broadcast never touches the database).
        """
        # Nobody may be subscribed to this conversation (subscriptions are
        # only requested once, at connect time) — nothing to deliver.
        participant_ids = self.subscriptions.get(conversation_id)
        if not participant_ids:
            return

        # Snapshot both levels: another socket's task may run while we await
        # a send and change either collection (e.g. a disconnect).
        for participant_id in list(participant_ids):
            for websocket_message in frames.get(participant_id, ()):
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
        
    async def _on_agent_flush(self, conversation_id: UUID, batch: list[tuple[UUID, str]]) -> None:
        """Route a finished owner burst by the owner's role (H-3: the harness is
        role-agnostic; the route lives in the handler).

          - owner is a staff/volunteer user -> free-form reply via `converse`,
            broadcast as the assistant (#500 V-1..V-5)
          - owner is a client              -> intent classification (#501); a no-op
            in #500

        Each batch entry is (message_id, body): the bodies go to the agent, the
        ids let us act on exactly the messages it answered. On a reply we persist
        it as a Message sent by the assistant (AS-4) and broadcast it to the
        conversation, and mark the burst it answered read by the assistant
        (V-6); on `None` (no model, Ollama down, timeout, empty) we do nothing
        (H-5). The
        AI-mark is implicit: the sender is the assistant. Best-effort and
        non-blocking (H-2): the flush runs in its own session, closed before the
        broadcast, so the base human chat is never affected.
        """
        websocket_message = None
        mark_read_message = None
        async with session_scope() as db:
            conversation = db.scalar(
                select(models.Conversation).where(models.Conversation.id == conversation_id)
            )
            if conversation is None:
                return
            owner = conversation.initiatorParticipant
            if owner is None:
                return

            # Both routes send as the stable assistant identity (AS-4). If it's
            # missing we can't act at all, so no-op before making any LLM call.
            assistant = get_user_by_username(AI_AGENT_USERNAME, db=db)
            if assistant is None or assistant.participantId is None:
                if not PRODUCTION:
                    print(f"agent flush: no assistant ({AI_AGENT_USERNAME}) participant found -> nothing")
                return

            bodies = [body for _, body in batch]

            if owner.user is not None:
                # Volunteer free-form route (#500 V-1..V-5). V-2: converse with the
                # shared persona (bodies only); returns a reply or None. converse()
                # re-checks the model (A-4), so a model cleared after the harness
                # gate still safely no-ops here.
                reply = await converse(db=db, messages=bodies, context=None)
                intent = None
            else:
                # Client intent route (#501): classify the burst (C-1) and dispatch to
                # a code handler (C-2/C-3) or the free-form fallback (C-6).
                intent = await classify(db=db, messages=bodies)
                if intent is None:
                    # C-8: no model / Ollama down / timeout -> nothing happens, chat
                    # continues unaffected.
                    return
                reply = await resolve_reply(db=db, intent=intent, messages=bodies)

            if not reply:
                # No model (volunteer), or an intent that yields no reply (free-form
                # off, or a fragment with no data) -> nothing is said or marked
                # (C-8 / C-10).
                if not PRODUCTION:
                    who = owner.user.username if owner.user else "client"
                    print(f"agent flush: {who} burst, no reply (intent={intent}) -> nothing")
                return

            frames = self._compose_assistant_reply(
                db=db, conversation_id=conversation_id, batch=batch,
                assistant=assistant, reply=reply, intent=intent,
            )

        # The session is closed before the broadcast on purpose: no DB connection is
        # held open while sending to sockets (same as the human-message path above).
        if frames:
            await self.broadcast(conversation_id, frames)

    def _compose_assistant_reply(
        self, db: Session, conversation_id: UUID, batch: list[tuple[UUID, str]],
        assistant: models.User, reply: str, intent: str | None,
    ) -> dict[UUID, list[schemas.WebSocketMessage]]:
        """Persist an assistant auto-reply, mark the answered burst read, and build
        the per-recipient websocket frames to broadcast (V-6 / C-10) — shared by
        both routes so the send / mark-read / broadcast logic stays in one place
        and in sync.

        `intent` is recorded on the reply for audit (C-7). Each recipient gets
        their variant (staff: full — they see the assistant identity; client:
        stripped). Returns the per-recipient frame map (message frame plus the
        mark-read frame when the burst had unread messages), ready to broadcast.
        """
        message = models.Message(
            conversationId=conversation_id,
            sentByParticipantId=assistant.participantId,
            body=reply,
            intent=intent,
        )
        db.add(message)

        # The agent has read exactly this burst to produce the reply, so record
        # that: mark the burst's still-unread messages read by the assistant.
        read_on = datetime.now(timezone.utc)
        read_messages = db.scalars(
            select(models.Message)
            .where(
                models.Message.id.in_([message_id for message_id, _ in batch]),
                models.Message.readByParticipantId.is_(None),
            )
        ).all()
        read_message_ids = [m.id for m in read_messages]
        for m in read_messages:
            m.readByParticipantId = assistant.participantId
            m.readOn = read_on

        db.commit()
        db.refresh(message)

        staff_frames: list[schemas.WebSocketMessage] = [
            schemas.WebSocketChatMessage(
                command=schemas.WebSocketCommand.MESSAGE,
                payload=message_payload(message, include_participants=True),
            )
        ]
        client_frames: list[schemas.WebSocketMessage] = [
            schemas.WebSocketChatMessage(
                command=schemas.WebSocketCommand.MESSAGE,
                payload=message_payload(message),
            )
        ]
        if read_message_ids:
            # Tell live recipients the owner's burst is read so the picker's
            # unread badge clears (same protocol as a human's mark_read).
            # `assistant` is the User (not its participant), so the staff
            # variant's nested participant is built from its plain columns.
            staff_frames.append(schemas.WebSocketMarkRead(
                command=schemas.WebSocketCommand.MARK_READ,
                payload=schemas.WebsocketMarkReadPayload(
                    conversationId=conversation_id,
                    messageIds=read_message_ids,
                    participantId=assistant.participantId,
                    readOn=read_on,
                    readByParticipant=schemas.Participant(
                        id=assistant.participantId,
                        user=schemas.UserMinimal(id=assistant.id, username=assistant.username),
                    ),
                ),
            ))
            client_frames.append(schemas.WebSocketMarkRead(
                command=schemas.WebSocketCommand.MARK_READ,
                payload=schemas.WebsocketMarkReadPayload(
                    conversationId=conversation_id,
                    messageIds=read_message_ids,
                    participantId=assistant.participantId,
                    readOn=read_on,
                ),
            ))
        return self._recipient_frames(db, conversation_id, staff_frames, client_frames)

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
                        # Capture the id while the session is open: the harness
                        # buffers it so the agent flush can act on exactly this
                        # message (e.g. mark it read, V-6).
                        message_id = message.id

                        staff_frames: list[schemas.WebSocketMessage] = [
                            schemas.WebSocketChatMessage(
                                command=schemas.WebSocketCommand.MESSAGE,
                                payload=message_payload(message, include_participants=True),
                            )
                        ]
                        client_frames: list[schemas.WebSocketMessage] = [
                            schemas.WebSocketChatMessage(
                                command=schemas.WebSocketCommand.MESSAGE,
                                payload=message_payload(message),
                            )
                        ]
                        frames = self._recipient_frames(db, conversation_id, staff_frames, client_frames)
                    # The session is closed before the broadcast on purpose:
                    # no DB connection is held open while sending to sockets.

                    if frames:
                        await self.broadcast(conversation_id, frames)

                    # Best-effort Agent harness (#500): feed this message into the
                    # per-conversation debounce buffer (one burst per conversation,
                    # always the owner's). The window/cap are read from LlmSettings
                    # each message so admin edits apply live. Entirely best-effort —
                    # on any error we skip the agent and the base chat path above is
                    # unaffected.
                    try:
                        async with session_scope() as db:
                            llm = get_llm_settings(db=db)
                            # The harness reacts only to the chat's owner — a staff
                            # member in their own chat, or a client in theirs. It
                            # never reacts to the non-owner (a staff user serving a
                            # client's chat), whose messages are ordinary human chat.
                            owned = conversation_is_owned_by(
                                db=db, conversation_id=conversation_id, participant_id=participant.id)
                        # Engage the agent only for the owner, and only while it is
                        # active (a model is configured; A-4). Without either we skip
                        # buffering entirely — no state, timer, or fire — instead of
                        # engaging the pipeline only to end at converse() returning
                        # None. The agent's own fire-time check stays authoritative
                        # (the model could be cleared mid-burst).
                        if owned and llm is not None and (llm.model or "").strip():
                            self.agent_buffer.submit(
                                conversation_id=conversation_id,
                                message_id=message_id,
                                body=request.payload.body,
                                window_s=float(llm.debounceWindowSeconds),
                                cap=int(llm.debounceBatchCap),
                            )
                    except Exception as e:
                        if not PRODUCTION:
                            print(f"agent harness skipped: {e!r}")

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
                        
                        # Rebuilt (not re-validated from the request): staff get
                        # the nested "who marked it read", clients only the
                        # opaque ID (message_payload's rules).
                        # The ws `participant` is detached (bound to connect()'s
                        # now-closed session), so it must not be lazy-loaded:
                        # re-fetch it from the current session instead.
                        reader = get_participant_by_id(db=db, participant_id=participant.id)
                        base_payload = dict(
                            conversationId=request.payload.conversationId,
                            messageIds=request.payload.messageIds,
                            participantId=request.payload.participantId,
                            readOn=request.payload.readOn,
                        )
                        staff_frames = [
                            schemas.WebSocketMarkRead(
                                command=schemas.WebSocketCommand.MARK_READ,
                                payload=schemas.WebsocketMarkReadPayload(
                                    **base_payload,
                                    readByParticipant=(
                                        schemas.Participant.model_validate(
                                            reader, from_attributes=True
                                        )
                                        if reader is not None else None
                                    ),
                                ),
                            )
                        ]
                        client_frames = [
                            schemas.WebSocketMarkRead(
                                command=schemas.WebSocketCommand.MARK_READ,
                                payload=schemas.WebsocketMarkReadPayload(**base_payload),
                            )
                        ]
                        frames = self._recipient_frames(db, conversation_id, staff_frames, client_frames)

                    # The session is closed before the broadcast on purpose:
                    # no DB connection is held open while sending to sockets.

                    if frames:
                        await self.broadcast(conversation_id, frames)
                
                
            except Exception as e:
                print(e)
                await self.disconnect(socket_id, participant.id)
                break
        
    