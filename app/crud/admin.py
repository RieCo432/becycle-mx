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


def resolve_client_duplicate(db: Session, obsolete_client_id: UUID, valid_client_id: UUID) -> None:
    obsolete_client = get_client(db=db, client_id=obsolete_client_id)
    valid_client = get_client(db=db, client_id=valid_client_id)

    if obsolete_client is None or valid_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more clients not found!"})

    if not is_potential_client_duplicate_detected_before(db=db, client1=obsolete_client, client2=valid_client):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "These clients are not potential duplicates"})

    obsolete_client_contracts = get_contracts(db=db, client_id=obsolete_client_id)

    for contract in obsolete_client_contracts:
        contract.clientId = valid_client_id

    obsolete_client_appointments = get_appointments(db=db, client_id=obsolete_client_id)

    for appointment in obsolete_client_appointments:
        appointment.clientId = valid_client_id

    obsolete_client_logins = get_client_logins(db=db, client_id=obsolete_client_id)

    for login in obsolete_client_logins:
        db.delete(login)

    valid_client.preBecycleSurveyCompleted |= obsolete_client.preBecycleSurveyCompleted
    valid_client.periBecycleSurveyCompleted |= obsolete_client.periBecycleSurveyCompleted
    valid_client.postBecycleSurveyCompleted |= obsolete_client.postBecycleSurveyCompleted

    c1_id = str(obsolete_client_id)
    c2_id = str(valid_client_id)

    if c2_id < c1_id:
        temp = c1_id
        c1_id = c2_id
        c2_id = temp

    detected_client_duplicate = db.scalar(
        select(models.DetectedPotentialClientDuplicates)
        .where(
            (models.DetectedPotentialClientDuplicates.client1Id == c1_id)
            & (models.DetectedPotentialClientDuplicates.client2Id == c2_id)
        )
    )

    db.delete(detected_client_duplicate)

    db.delete(obsolete_client)

    db.commit()
