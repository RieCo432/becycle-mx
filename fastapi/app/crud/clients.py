import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_all_clients(db: Session) -> list[schemas.Client]:
    return [_ for _ in db.scalars(
        select(models.Client)
    )]


def get_clients(db: Session, first_name: str, last_name: str, email_address: str) -> list[models.Client]:
    clients = [_ for _ in db.scalars(
        select(models.Client)
        .where(
            (models.Client.firstName == first_name)
            | (models.Client.lastName == last_name)
            | (models.Client.emailAddress == email_address)
        )
    )]

    if len(clients) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "No clients"})

    return clients


def get_client(db: Session, client_id: UUID) -> models.Client:
    client = db.scalar(
        select(models.Client)
        .where(models.Client.id == client_id)
    )

    return client


def post_client(db: Session, client_data: schemas.ClientCreate) -> models.Client:
    client = models.Client(
        firstName=client_data.firstName.lower(),
        lastName=client_data.lastName.lower(),
        emailAddress=client_data.emailAddress.lower()
    )
    db.add(client)
    db.commit()
    return client


def post_client_temp(db: Session, client_data: schemas.ClientCreate) -> models.ClientTemp:
    client_temp = db.scalar(
        select(models.ClientTemp)
        .where(models.ClientTemp.emailAddress == client_data.emailAddress.lower())
    )

    # if the temp client already exists, delete it
    if client_temp is not None:
        db.delete(client_temp)
        db.commit()

    client_temp = models.ClientTemp(
        firstName=client_data.firstName.lower(),
        lastName=client_data.lastName.lower(),
        emailAddress=client_data.emailAddress.lower()
    )

    db.add(client_temp)
    db.commit()

    return client_temp


def verify_client_temp(db: Session, client_temp_id: UUID, verification_code: str) -> models.Client:
    client_temp = db.scalar(
        select(models.ClientTemp)
        .where(
            (models.ClientTemp.id == client_temp_id)
            & (models.ClientTemp.verificationCode == verification_code)
        )
    )

    if client_temp is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This code is invalid."})

    if datetime.datetime.utcnow() > client_temp.expirationDateTime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This action has expired."})

    client = models.Client(
        firstName=client_temp.firstName,
        lastName=client_temp.lastName,
        emailAddress=client_temp.emailAddress
    )
    db.add(client)
    db.delete(client_temp)
    db.commit()

    return client


def get_client_by_email(db: Session, email_address: str) -> models.Client:
    client = db.scalar(
        select(models.Client)
        .where(models.Client.emailAddress == email_address)
    )

    return client


def create_client_login_code(db: Session, client: models.Client) -> models.ClientLogin:
    client_login = models.ClientLogin(
        clientId=client.id
    )

    db.add(client_login)
    db.commit()

    return client_login


def authenticate_client(db: Session, client_id: UUID, login_code: str) -> models.Client:
    client_login = db.scalars(
        select(models.ClientLogin)
        .where(models.ClientLogin.clientId == client_id)
        .order_by(models.ClientLogin.expirationDateTime.desc())
    ).first()

    if client_login is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "This ID does not correspond to any client, or this client has not requested a login!"})

    if login_code != client_login.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This code is not valid."})
    if datetime.datetime.utcnow() > client_login.expirationDateTime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This code has expired."})

    client = get_client(db=db, client_id=client_login.clientId)

    db.delete(client_login)
    db.commit()

    return client


def get_similar_email_addresses(db: Session, email_address: str) -> list[str]:
    similar_email_addresses = [_ for _ in db.scalars(
        select(models.Client.emailAddress)
        .where(models.Client.emailAddress.startswith(email_address))
    )]

    return similar_email_addresses


def get_potential_client_matches(db: Session, first_name: str | None, last_name: str | None, email_address: str | None, max_distance: int = 10) -> list[models.Client]:
    query_filter = []
    if first_name is not None and first_name != "":
        query_filter.append(models.Client.firstName.contains(first_name) | (func.levenshtein(models.Client.firstName, first_name) <= max_distance))
    if last_name is not None and last_name != "":
        query_filter.append(models.Client.lastName.contains(last_name) | (func.levenshtein(models.Client.lastName, last_name) <= max_distance))
    if email_address is not None and email_address != "":
        query_filter.append(models.Client.emailAddress.contains(email_address) | (func.levenshtein(models.Client.emailAddress, email_address) <= max_distance))

    potential_matches = [_ for _ in db.scalars(
            select(models.Client)
            .where(and_(*query_filter))
        )]

    return potential_matches


def update_client(db: Session, client_id: UUID, new_first_name: str, new_last_name: str, new_email_address: str | None = None):
    client = get_client(db=db, client_id=client_id)
    client.firstName = new_first_name.lower()
    client.lastName = new_last_name.lower()

    if new_email_address is not None:
        client.emailAddress = new_email_address.lower()

    db.commit()

    return client


def get_client_logins(db: Session, client_id: UUID) -> list[models.ClientLogin]:
    return [_ for _ in db.scalars(
        select(models.ClientLogin)
        .where(models.ClientLogin.clientId == client_id)
    )]
