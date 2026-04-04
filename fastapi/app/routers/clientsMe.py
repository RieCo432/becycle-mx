from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas
from app.services.accounts_helpers import AccountTypes

clients_me = APIRouter(
    tags=["clients"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_client)],
    responses={404: {"description": "Not Found"}}
)


@clients_me.get("/clients/me")
async def get_client_me(client: Annotated[models.Client, Depends(dep.get_current_client)]) -> schemas.Client:
    return client


@clients_me.patch("/clients/me")
async def update_client_me(
        new_names: schemas.ClientChangeName,
        client: Annotated[models.Client, Depends(dep.get_current_client)],
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    client = crud.update_client(db=db, client_id=client.id, new_first_name=new_names.firstName, new_last_name=new_names.lastName)

    return client


@clients_me.get("/clients/me/contracts")
async def get_my_contracts(
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> list[schemas.ContractRestricted]:
    return crud.get_client_restricted_contracts(db=db, client_id=client.id)


@clients_me.get("/clients/me/contracts/{contract_id}")
async def get_my_contract(
        contract_id: UUID,
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> schemas.ContractRestricted:
    return crud.get_client_restricted_contract(db=db, client_id=client.id, contract_id=contract_id)


@clients_me.get("/clients/me/appointments")
async def get_my_appointments(
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> list[schemas.Appointment]:
    return crud.get_appointments(db=db, client_id=client.id)


@clients_me.post("/clients/me/appointments/request")
async def request_appointment(
        appointment_request_data: schemas.AppointmentRequest,
        client: Annotated[models.Client, Depends(dep.get_current_client)],
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment_create_data = schemas.AppointmentCreate(
        typeId=appointment_request_data.typeId,
        startDateTime=appointment_request_data.startDateTime,
        notes=appointment_request_data.notes,
        clientId=client.id
    )

    appointment = crud.create_appointment(db=db, appointment_data=appointment_create_data)

    email_tasks.add_task(appointment.send_request_received_email)

    return appointment


@clients_me.patch("/clients/me/appointments/{appointment_id}/cancel")
async def cancel_my_appointment(
        appointment_id: UUID,
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:
    return crud.cancel_my_appointment(db=db, client=client, appointment_id=appointment_id)


@clients_me.get("/clients/me/bikes/{bike_id}")
async def get_bike(
        bike_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.get_bike(db=db, bike_id=bike_id)