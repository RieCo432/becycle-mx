from fastapi import APIRouter, Depends
import app.models as models
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated
from uuid import UUID


appointments = APIRouter(
    tags=["appointments"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@appointments.post("/appointment/request")
async def request_appointment(
        appointment_data: schemas.AppointmentRequest,
        client: Annotated[models.Client, Depends(dep.get_current_client)],
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    return crud.request_appointment(db=db, appointment_data=appointment_data, client_id=client.id)


@appointments.post("/appointment", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def create_appointment(
        appointment_data: schemas.AppointmentCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    return crud.create_appointment(db=db, appointment_data=appointment_data)


@appointments.patch("/appointments/{appointment_id}/confirm", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def confirm_appointment(
        appointment_id: UUID,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    return crud.confirm_appointment(db=db, appointment_id=appointment_id)

@appointments.patch("/appointments/{appointment_id}/cancel", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def cancel_appointment(
        appointment_id: UUID,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    return crud.cancel_appointment(db=db, appointment_id=appointment_id)

