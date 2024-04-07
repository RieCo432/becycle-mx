from uuid import UUID

from fastapi import HTTPException, status

import app.schemas as schemas
import app.models as models
from Levenshtein import distance as levenshtein_distance
from sqlalchemy import select
from sqlalchemy.orm import Session
from .clients import get_all_clients, get_client, get_client_logins
from .contracts import get_contracts
from .appointments import get_appointments


def get_potential_client_duplicates_detected(db: Session) -> list[models.DetectedPotentialClientDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .order_by(models.DetectedPotentialClientDuplicates.similarityScore)
    )]


def is_potential_client_duplicate_detected_before(db: Session, client1: models.Client, client2: models.Client) -> bool:
    if not str(client1.id) < str(client2.id):
        temp = client1
        client1 = client2
        client2 = temp

    return len([_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .where(
            (models.DetectedPotentialClientDuplicates.client1Id == client1.id)
            & (models.DetectedPotentialClientDuplicates.client2Id == client2.id)
        )
    )]) > 0


def find_potential_client_duplicates(db: Session) -> None:
    clients = get_all_clients(db=db)

    for i in range(len(clients)):

        client1 = clients[i]

        if client1.firstName.lower() == "notprovided" and client1.lastName.lower() == "notprovided":
            continue

        for j in range(i+1, len(clients)):

            client2 = clients[j]

            if client2.firstName.lower() == "notprovided" and client2.lastName.lower() == "notprovided":
                continue

            if client1.id == client2.id:
                continue

            if is_potential_client_duplicate_detected_before(db=db, client1=client1, client2=client2):
                continue

            similarity_score = 0

            client_1_all_names = [n.strip().lower() for n in client1.firstName.split(" ") + client1.lastName.split(" ")]
            client_2_all_names = [n.strip().lower() for n in client2.firstName.split(" ") + client2.lastName.split(" ")]

            for client_1_name in client_1_all_names:
                if len(client_1_name) < 3:
                    continue
                for client_2_name in client_2_all_names:
                    if len(client_2_name) < 3:
                        continue
                    if client_1_name == client_2_name:
                        similarity_score += 2
                    elif levenshtein_distance(client_1_name, client_2_name) < 4:
                        similarity_score += 1

            client_1_email = client1.emailAddress.lower().replace(" ", "")
            client_2_email = client2.emailAddress.lower().replace(" ", "")

            if client_1_email == client_2_email:
                similarity_score += 2
            elif levenshtein_distance(client_1_email, client_2_email) < 4:
                similarity_score += 1

            if similarity_score >= 2:
                c1_id = client1.id
                c2_id = client2.id
                if str(c2_id) < str(c1_id):
                    temp = c1_id
                    c1_id = c2_id
                    c2_id = temp
                potential_duplicate = models.DetectedPotentialClientDuplicates(
                    client1Id=c1_id,
                    client2Id=c2_id,
                    similarityScore=similarity_score
                )
                db.add(potential_duplicate)
                db.commit()


def get_potential_client_duplicate(db: Session, potential_client_duplicate_id: UUID) -> models.DetectedPotentialClientDuplicates:
    return db.scalar(
        select(models.DetectedPotentialClientDuplicates)
        .where(models.DetectedPotentialClientDuplicates.id == potential_client_duplicate_id)
    )


def get_potential_client_duplicates_for_client(db: Session, client_id: UUID) -> list[models.DetectedPotentialClientDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .where(
            (models.DetectedPotentialClientDuplicates.client1Id == client_id)
            | (models.DetectedPotentialClientDuplicates.client2Id == client_id)
        )
    )]


def resolve_client_duplicate(db: Session, potential_client_duplicate_id: UUID, discard_client_id: UUID, keep_client_id: UUID) -> None:
    potential_client_duplicate = get_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)

    if potential_client_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential client duplicate not found"})

    if (
            (potential_client_duplicate.client1Id != discard_client_id and potential_client_duplicate.client1Id != keep_client_id)
            or (potential_client_duplicate.client2Id != discard_client_id and potential_client_duplicate.client2Id != keep_client_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "One of the clients is not part of this potential duplicate"})

    discard_client = get_client(db=db, client_id=discard_client_id)
    keep_client = get_client(db=db, client_id=keep_client_id)

    if discard_client is None or keep_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more clients not found!"})

    obsolete_client_contracts = get_contracts(db=db, client_id=discard_client_id)

    for contract in obsolete_client_contracts:
        contract.clientId = keep_client_id

    obsolete_client_appointments = get_appointments(db=db, client_id=discard_client_id)

    for appointment in obsolete_client_appointments:
        appointment.clientId = keep_client_id

    obsolete_client_logins = get_client_logins(db=db, client_id=discard_client_id)

    for login in obsolete_client_logins:
        db.delete(login)

    db.commit()

    keep_client.preBecycleSurveyCompleted |= discard_client.preBecycleSurveyCompleted
    keep_client.periBecycleSurveyCompleted |= discard_client.periBecycleSurveyCompleted
    keep_client.postBecycleSurveyCompleted |= discard_client.postBecycleSurveyCompleted

    db.delete(potential_client_duplicate)
    db.commit()

    for potential_client_duplicate_other in get_potential_client_duplicates_for_client(db=db, client_id=discard_client_id):
        db.delete(potential_client_duplicate_other)
    db.commit()

    db.delete(discard_client)

    db.commit()


def ignore_potential_client_duplicate(db: Session, potential_client_duplicate_id: UUID) -> models.DetectedPotentialClientDuplicates:
    potential_client_duplicate = get_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)
    if potential_client_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential client duplicate not found"})

    potential_client_duplicate.ignore = True

    db.commit()

    return potential_client_duplicate
