import os
from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas
from app import auth


clients = APIRouter(
    tags=["clients"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@clients.get("/clients", dependencies=[Depends(dep.get_current_active_user)])
async def get_clients(
            first_name: str = None,
            last_name: str = None,
            email_address: str = None,
            db: Session = Depends(dep.get_db)) -> list[schemas.Client]:
    return crud.get_clients(db=db, first_name=first_name, last_name=last_name, email_address=email_address)


@clients.get("/client/id-by-email", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_id_by_email(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> dict[str, UUID]:

    client = crud.get_client_by_email(db=db, email_address=email_address)
    return {"id": client.id}


@clients.get("/clients/email-address-suggestions", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_email_address_suggestions(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> list[str]:
    return crud.get_similar_email_addresses(email_address=email_address, db=db)


@clients.post("/client", dependencies=[Depends(dep.get_current_active_user)])
async def create_client(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    return crud.post_client(db=db, client_data=client_data)


@clients.post("/client/temp")
async def create_client_temp(
        client_data: schemas.ClientCreate,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.ClientTemp:

    client_temp = crud.post_client_temp(db=db, client_data=client_data)

    email_tasks.add_task(client_temp.send_email_verification_link)

    return client_temp


@clients.post("/client/temp/verify")
async def verify_client_temp(
        client_temp_id: Annotated[UUID, Form()],
        verification_code: Annotated[str, Form()],
        db: Session = Depends(dep.get_db)) -> schemas.Token:

    client = crud.verify_client_temp(db=db, client_temp_id=client_temp_id, verification_code=verification_code)

    access_token = auth.create_access_token(data={"sub": str(client.id)})

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


@clients.get("/client/login-code")
async def get_client_login_code(
        email_address: str,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.ClientPreAuth:

    client = crud.get_client_by_email(db=db, email_address=email_address.lower())

    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "There is no client associated with this email address."})

    client_login = crud.create_client_login_code(db=db, client=client)

    email_tasks.add_task(client_login.send_login_code)

    return schemas.ClientPreAuth(
        id=client.id
    )


@clients.post("/clients/token")
async def get_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)) -> schemas.Token:

    client = crud.authenticate_client(db=db, client_id=UUID(form_data.username), login_code=form_data.password)

    access_token = auth.create_access_token(data={"sub": str(client.id)})

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


@clients.get("/clients/find", dependencies=[Depends(dep.get_current_active_user)])
async def find_client(
        first_name: str = None,
        last_name: str = None,
        email_address: str = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.Client]:
    return crud.get_potential_client_matches(db=db, first_name=first_name, last_name=last_name, email_address=email_address)


@clients.get("/clients/me")
async def get_client_me(client: Annotated[models.Client, Depends(dep.get_current_client)]) -> schemas.Client:

    return client


@clients.patch("/clients/me")
async def update_client_me(
        new_names: schemas.ClientChangeName,
        client: Annotated[models.Client, Depends(dep.get_current_client)],
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    client = crud.update_client(db=db, client_id=client.id, new_first_name=new_names.firstName, new_last_name=new_names.lastName)

    return client


# TODO: Implement query parameters for pagination
@clients.get("/clients/me/contracts")
async def get_my_contracts(
        open: bool = True,
        closed: bool = True,
        expired: bool = True,
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, client_id=client.id, open=open, closed=closed, expired=expired)


@clients.get("/clients/me/contracts/{contract_id}")
async def get_my_contract(
        contract_id: UUID,
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> schemas.ContractRestricted:
    contract = crud.get_client_contract(db=db, client_id=client.id, contract_id=contract_id)

    return schemas.ContractRestricted(
        workingUsername=contract.workingUser.username,
        checkingUsername=contract.checkingUser.username,
        depositCollectingUsername=contract.depositCollectingUser.username,
        returnAcceptingUsername=contract.returnAcceptingUser.username if contract.returnAcceptingUser else None,
        depositReturningUsername=contract.depositReturningUser.username if contract.depositReturningUser else None,
        id=contract.id,
        startDate=contract.startDate,
        endDate=contract.endDate,
        returnedDate=contract.returnedDate,
        depositAmountReturned=contract.depositAmountReturned,
        detailsSent=contract.detailsSent,
        expiryReminderSent=contract.expiryReminderSent,
        returnDetailsSent=contract.returnDetailsSent,
        clientId=contract.clientId,
        bikeId=contract.bikeId,
        depositAmountCollected=contract.depositAmountCollected,
        conditionOfBike=contract.conditionOfBike,
        contractType=contract.contractType,
        notes=contract.notes
    )


# TODO: Implement query parameters for pagination
@clients.get("/clients/me/appointments")
async def get_my_appointments(
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> list[schemas.Appointment]:
    return crud.get_appointments(db=db, client_id=client.id)


@clients.patch("/clients/me/appointments/{appointment_id}/cancel")
async def cancel_my_appointment(
        appointment_id: UUID,
        client: models.Client = Depends(dep.get_current_client),
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:
    return crud.cancel_my_appointment(db=db, client=client, appointment_id=appointment_id)


@clients.get("/clients/{client_id}", dependencies=[Depends(dep.get_current_active_user)])
async def get_client(client_id: UUID,
                     db: Session = Depends(dep.get_db)) -> schemas.Client:
    return crud.get_client(db=db, client_id=client_id)


@clients.patch("/clients/{client_id}", dependencies=[Depends(dep.get_current_active_user)])
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
@clients.get("/clients/{client_id}/contracts", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_contracts(
        client_id: UUID,
        open: bool = True,
        closed: bool = True,
        expired: bool = True,
        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, client_id=client_id, open=open, closed=closed, expired=expired)


# TODO: Implement query parameters for pagination
@clients.get("/clients/{client_id}/appointments", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_appointments(
        client_id: UUID,
        db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentFull]:
    return crud.get_appointments(db=db, client_id=client_id)
