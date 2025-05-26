from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas


clients = APIRouter(
    tags=["clients"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@clients.get("/clients")
async def get_clients(
            first_name: str = None,
            last_name: str = None,
            email_address: str = None,
            db: Session = Depends(dep.get_db)) -> list[schemas.Client]:
    return crud.get_clients(db=db, first_name=first_name, last_name=last_name, email_address=email_address)


@clients.get("/clients/id-by-email")
async def get_client_id_by_email(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> dict[str, UUID]:

    client = crud.get_client_by_email(db=db, email_address=email_address)
    return {"id": client.id}


@clients.get("/clients/email-address-suggestions")
async def get_client_email_address_suggestions(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> list[str]:
    return crud.get_similar_email_addresses(email_address=email_address, db=db)


@clients.post("/clients")
async def create_client(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    return crud.post_client(db=db, client_data=client_data)


@clients.get("/clients/find")
async def find_client(
        first_name: str = None,
        last_name: str = None,
        email_address: str = None,
        max_distance: int = 10,
        db: Session = Depends(dep.get_db)) -> list[schemas.Client]:
    return crud.get_potential_client_matches(db=db, first_name=first_name, last_name=last_name, email_address=email_address, max_distance=max_distance)


@clients.get("/clients/{client_id}")
async def get_client(client_id: UUID,
                     db: Session = Depends(dep.get_db)) -> schemas.Client:
    return crud.get_client(db=db, client_id=client_id)


@clients.patch("/clients/{client_id}")
async def update_client_full(
        client_id: UUID,
        updated_client_data: schemas.ClientBase,
        db: Session = Depends(dep.get_db)
) -> schemas.Client:
    return crud.update_client(db=db,
                              client_id=client_id,
                              new_first_name=updated_client_data.firstName,
                              new_last_name=updated_client_data.lastName,
                              new_email_address=updated_client_data.emailAddress)


# TODO: Implement query parameters for pagination
@clients.get("/clients/{client_id}/contracts")
async def get_client_contracts(
        client_id: UUID,
        open: bool = True,
        closed: bool = True,
        expired: bool = True,
        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, client_id=client_id, open=open, closed=closed, expired=expired)


# TODO: Implement query parameters for pagination
@clients.get("/clients/{client_id}/appointments")
async def get_client_appointments(
        client_id: UUID,
        db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentFull]:
    return crud.get_appointments(db=db, client_id=client_id)
