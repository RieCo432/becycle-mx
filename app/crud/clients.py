from sqlalchemy import select
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas


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

