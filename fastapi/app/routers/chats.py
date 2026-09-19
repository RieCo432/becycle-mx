from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks
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
    return crud.get_or_create_conversation(participant=participant, db=db)


@chats.get("/chats/participants/me")
async def get_my_participant(
        participant: models.Participant = Depends(dep.get_current_participant),
        db: Session = Depends(dep.get_db)
) -> schemas.Participant:
    return participant


