from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from starlette.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app import auth
import app.models as models


chats = APIRouter(
    tags=["chats"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)

# Built on first use (inside a running event loop): ChatManager.__init__
# schedules a background task, which asyncio.create_task requires a live
# loop for, so the manager cannot be constructed at import time.
_chat_manager: "crud.ChatManager | None" = None


def _ensure_chat_manager() -> "crud.ChatManager":
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = crud.ChatManager()
    return _chat_manager


@chats.get("/chats/conversations", dependencies=[Depends(dep.check_permissions)])
async def get_conversations(
        db: Session = Depends(dep.get_db)
) -> list[schemas.Conversation]:
    return crud.get_conversations(db=db)


@chats.get("/chats/conversations/my")
async def get_my_conversation(
        participant: models.Participant = Depends(dep.get_current_participant),
        db: Session = Depends(dep.get_db)
) -> schemas.Conversation:
    conversation, created = crud.get_or_create_conversation(participant=participant, db=db)
    if created:
        # Push the newcomer to the staff who are online right now (their
        # REST list is otherwise static). Best-effort: a failed push must
        # not fail the request — staff catch up on their next (re)connect.
        try:
            await _ensure_chat_manager().notify_new_conversation(
                conversation=schemas.Conversation.model_validate(conversation, from_attributes=True)
            )
        except Exception as e:
            print(f"failed to notify about new conversation {conversation.id}: {e}")
    return conversation


@chats.get("/chats/participants/me")
async def get_my_participant(
        participant: models.Participant = Depends(dep.get_current_participant),
        db: Session = Depends(dep.get_db)
) -> schemas.Participant:
    return participant

@chats.websocket("/chats/ws")
async def websocket_endpoint(
        websocket: WebSocket,
):
    socket_id = None
    participant = None
    try:
        chat_manager = _ensure_chat_manager()
        socket_id, participant = await chat_manager.connect(websocket=websocket)
        await chat_manager.take_it_from_here(socket_id, participant)
    except WebSocketDisconnect:
        # The client went away (before sending a token, or mid-session).
        # `take_it_from_here` cleaned up its own socket on the way out, and
        # an accepted-but-never-serviced connection has nothing to release.
        pass
    except Exception as e:
        print(e)
        # A failed handshake must not leave an accepted-but-unserviced
        # connection open. `connect` already closed with the auth-failure
        # code when the socket was still alive; this is the safety net for
        # everything else.
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        # Whatever the path out, a registered socket must not be left in
        # the manager's registries (disconnect is idempotent).
        if socket_id is not None and participant is not None:
            try:
                await _ensure_chat_manager().disconnect(socket_id, participant.id)
            except Exception as e:
                print(f"cleanup for socket {socket_id} failed: {e}")


