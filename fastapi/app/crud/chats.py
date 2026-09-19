import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


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