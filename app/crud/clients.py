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


def post_client(db: Session, client_to_create: schemas.ClientCreate) -> models.Client:
    client = models.Client(firstName=client_to_create.firstName, lastName=client_to_create.lastName, emailAddress=client_to_create.emailAddress)
    db.add(client)
    db.commit()
    return client

