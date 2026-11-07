from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
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

manager = crud.ChatManager()


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
            await manager.notify_new_conversation(
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
    try: 
        socket_id, participant = await manager.connect(websocket=websocket)
        await manager.take_it_from_here(socket_id, participant)
    except Exception as e:
        print(e)
        # await websocket.close()


