import uuid
from datetime import datetime, time, date
from typing import Annotated
from uuid import UUID

from dateutil import relativedelta
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

appointments = APIRouter(
    tags=["appointments"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@appointments.post("/appointments/request")
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


@appointments.post("/appointments/new", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def create_appointment(
        appointment_data: schemas.AppointmentCreate,
        email_tasks: BackgroundTasks,
        ignore_limits: bool = False,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.create_appointment(db=db, appointment_data=appointment_data, auto_confirm=True, ignore_limits=ignore_limits)

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


@appointments.get("/appointments")
async def get_appointment_via_hyperlink(
        appointment_id: UUID,
        client_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.AppointmentFull:
    crud.verify_appointment_hyperlink_parameters(db=db, appointment_id=appointment_id, client_id=client_id)
    return crud.get_appointment(db=db, appointment_id=appointment_id)


@appointments.patch("/appointments/cancel")
async def cancel_appointment_via_hyperlink(
        appointment_id: UUID,
        client_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.verify_appointment_hyperlink_parameters(db=db, appointment_id=appointment_id, client_id=client_id)
    appointment = crud.cancel_appointment(db=db, appointment_id=appointment_id)

    email_tasks.add_task(appointment.send_client_cancellation_email)



@appointments.get("/appointments/available")
async def get_available_appointments(
        appointment_type_id: str,
        ignore_limits: bool = False,
        db: Session = Depends(dep.get_db)) -> dict[date, list[dict]]:
    if ignore_limits:
        Depends(dep.get_current_appointment_manager_user)
    available_slots = crud.get_available_start_dates_and_times_for_appointment_type(db=db, appointment_type_id=appointment_type_id, ignore_limits=ignore_limits)

    return available_slots


@appointments.get("/appointments/types")
async def get_appointment_types(inactive: bool = False, db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentType]:
    return crud.get_appointment_types(db=db, inactive=inactive)


@appointments.post("/appointments/types", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def create_appointment_type(new_appointment_type: schemas.AppointmentType, db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    return crud.create_appointment_type(db=db, appointment_type_data=new_appointment_type)


@appointments.get("/appointments/types/{type_id}")
async def get_appointment_type(type_id: str, db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    return crud.get_appointment_type(db=db, appointment_type_id=type_id)


@appointments.patch("/appointments/types/{type_id}", dependencies=[Depends(dep.get_current_appointment_manager_user)])
async def update_appointment_type(
        type_id: str,
        updated_appointment_type_data: schemas.PatchAppointmentType,
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    appointment_type = crud.get_appointment_type(db=db, appointment_type_id=type_id)
    return crud.update_appointment_type(db=db, appointment_type=appointment_type, updated_appointment_type_data=updated_appointment_type_data)


@appointments.get("/appointments/calendar", dependencies=[Depends(dep.get_current_active_user)])
async def get_appointments(
        start_datetime: datetime = datetime.utcnow(),
        end_datetime: datetime = datetime.utcnow() + relativedelta.relativedelta(weeks=1),
        db: Session = Depends(dep.get_db)) -> list[schemas.Appointment]:
    booked_appointments = crud.get_appointments(db=db, start_datetime=start_datetime, end_datetime=end_datetime)
    closed_days = crud.get_closed_days(db=db, start_date=start_datetime.date(), end_date=end_datetime.date())

    for closed_day in closed_days:
        booked_appointments.append(schemas.Appointment(
            id=uuid.uuid4(),
            typeId='closedDay',
            startDateTime=datetime.combine(closed_day.date, time(hour=0, minute=0, second=0)),
            endDateTime=datetime.combine(closed_day.date, time(hour=23, minute=59, second=59)),
            notes=closed_day.note,
            clientId=uuid.uuid4()
        ))

    return booked_appointments
