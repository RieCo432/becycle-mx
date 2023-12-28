import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from uuid import UUID


def get_clients(db: Session, first_name: str, last_name: str, email_address: str) -> list[models.Client]:
    return [_ for _ in db.scalars(
        select(models.Client)
        .where(
            (models.Client.firstName == first_name)
            | (models.Client.lastName == last_name)
            | (models.Client.emailAddress == email_address)
        )
    )]


def post_client(db: Session, client_data: schemas.ClientCreate) -> models.Client:
    client = models.Client(
        firstName=client_data.firstName,
        lastName=client_data.lastName,
        emailAddress=client_data.emailAddress
    )
    db.add(client)
    db.commit()
    return client


def post_client_temp(db: Session, client_data: schemas.ClientCreate) -> models.ClientTemp:
    client_temp = models.ClientTemp(
        firstName=client_data.firstName,
        lastName=client_data.lastName,
        emailAddress=client_data.emailAddress
    )
    db.add(client_temp)
    db.commit()
    return client_temp


def verify_client_temp(db: Session, client_temp_id: UUID, verification_code: str) -> models.Client:
    client_temp = db.get(models.ClientTemp, client_temp_id)

    if client_temp is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This action has expired, or this client does not exist."})

    if datetime.datetime.utcnow() > client_temp.expirationDateTime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This action has expired."})

    if verification_code != client_temp.verificationCode:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Invalid Code."})

    client = models.Client(
        firstName=client_temp.firstName,
        lastName=client_temp.lastName,
        emailAddress=client_temp.emailAddress
    )
    db.add(client)
    db.delete(client_temp)
    db.commit()

    return client


