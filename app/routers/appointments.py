from fastapi import APIRouter, Depends, BackgroundTasks
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
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.request_appointment(db=db, appointment_data=appointment_data, client_id=client.id)

    email_tasks.add_task(appointment.send_request_received_email)

    return appointment


@appointments.post("/appointment", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def create_appointment(
        appointment_data: schemas.AppointmentCreate,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.create_appointment(db=db, appointment_data=appointment_data)

    email_tasks.add_task(appointment.send_confirmation_email)

    return appointment


@appointments.patch("/appointments/{appointment_id}/confirm", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def confirm_appointment(
        appointment_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.confirm_appointment(db=db, appointment_id=appointment_id)

    email_tasks.add_task(appointment.send_confirmation_email)

    return appointment


@appointments.patch("/appointments/{appointment_id}/cancel", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def cancel_appointment(
        appointment_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.cancel_appointment(db=db, appointment_id=appointment_id)

    if appointment.confirmed:
        email_tasks.add_task(appointment.send_cancellation_email)
    else:
        email_tasks.add_task(appointment.send_request_denied_email)

    return appointment

