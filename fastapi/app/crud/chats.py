from uuid import uuid4, UUID

from pydantic import TypeAdapter
from sqlalchemy import select

from fastapi import WebSocket
from starlette.exceptions import WebSocketException
from starlette.websockets import WebSocketState

import app.models as models
import app.schemas as schemas
import os

import sqlalchemy.exc
from fastapi import HTTPException, status

from jose import jwt, JWTError
from sqlalchemy.orm import Session


from app.database.db import SessionLocal
from services import WebSocketCommand

API_SECRET = os.environ['API_SECRET']
API_SECRET_ALGORITHM = os.environ['API_SECRET_ALGORITHM']


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


def get_or_create_conversation(db: Session, participant: models.Participant) -> models.Conversation:
    conversation = db.scalar(
        select(models.Conversation)
        .where(models.Conversation.initiatorParticipantId == participant.id)
    )
    
    if conversation is None:
        conversation = models.Conversation(
            initiatorParticipantId=participant.id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
    return conversation


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


websocket_message_adapter = TypeAdapter(schemas.WebSocketMessage)

class ChatManager:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.active_connections: dict[UUID, WebSocket] = {}
        self.participant_sockets: dict[UUID, list[UUID]] = {}
        self.subscriptions: dict[UUID, set[UUID]] = {}
        

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        token_message = await websocket.receive_json()
        participant = get_participant_by_token(token=token_message["token"], db=self.db)
        if participant is None:
            raise WebSocketException
        if participant.id not in self.participant_sockets:
            self.participant_sockets[participant.id] = []
            
        socket_id = uuid4()
        self.active_connections[socket_id] = websocket
        self.participant_sockets[participant.id].append(socket_id)
        
        print("Active connections:", len(self.active_connections))
        return socket_id, participant
    
    def subscribe(self, conversation_id: UUID, participant_id: UUID):
        if conversation_id not in self.subscriptions:
            self.subscriptions[conversation_id] = set()
        self.subscriptions[conversation_id].add(participant_id)
        
    async def broadcast(self, message: models.Message):
        for participant_id in self.subscriptions[message.conversationId]:
            for websocket_id in self.participant_sockets[participant_id]:
                websocket = self.active_connections[websocket_id]
                websocket_message = schemas.WebSocketChatMessage(
                    command=schemas.WebSocketCommand.MESSAGE,
                    payload=schemas.MessageBase.model_validate(message, from_attributes=True)
                )
                await send_websocket_message(websocket, websocket_message)

    async def disconnect(self, socket_id: UUID, participant_id: UUID):
        if self.active_connections[socket_id] is not None and self.active_connections[socket_id].state == WebSocketState.CONNECTED:
            print("Closing connection for participant:", participant_id)
            await self.active_connections[participant_id].close()
        
        self.participant_sockets[participant_id].remove(socket_id)
        del self.active_connections[socket_id]
        print("Active connections:", len(self.active_connections))
        
        
    async def take_it_from_here(self, socket_id: UUID, participant: models.Participant):
        socket = self.active_connections[socket_id]
        while True:
            try:
                request_json = await socket.receive_text()  
                request: schemas.WebSocketMessage = websocket_message_adapter.validate_json(request_json)
                
                if isinstance(request, schemas.WebSocketSubscribe):
                    subscribe_errors = []
                    for id in request.payload.conversationIds:
                        try:
                            assert isinstance(id, UUID)
                            self.subscribe(conversation_id=id, participant_id=participant.id)  
                        except Exception as e:
                            subscribe_errors.append(id)
                            
                elif isinstance(request, schemas.WebSocketChatMessage):
                    message = models.Message(
                        conversationId=request.payload.conversationId,
                        sentByParticipantId=participant.id,
                        body=request.payload.body)
                    self.db.add(message)
                    self.db.commit()
                    self.db.refresh(message)
                    await self.broadcast(message)
                    
                elif isinstance(request, schemas.WebSocketPing):
                    print(socket_id, "ping")
                    await send_websocket_message(socket, schemas.WebSocketPong(command=schemas.WebSocketCommand.PONG))
                            
                
                
                
            except Exception as e:
                print(e)
                await self.disconnect(socket_id, participant.id)
                break
        
    