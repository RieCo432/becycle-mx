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


def get_client(db: Session, client_id: UUID) -> models.Client:
    client = db.scalar(
        select(models.Client)
        .where(models.Client.id == client_id)
    )

    return client


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This code is not valid."})

    client = get_client(db=db, client_id=client_login.clientId)

    if client is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Some unknown error has occured!"})

    db.delete(client_login)
    db.commit()

    return client




