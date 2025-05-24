from datetime import datetime
from uuid import UUID
from dateutil import relativedelta
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

appointments = APIRouter(
    tags=["appointments"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@appointments.post("/appointments/new")
async def create_appointment(
        appointment_data: schemas.AppointmentCreate,
        email_tasks: BackgroundTasks,
        ignore_limits: bool = False,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.create_appointment(db=db, appointment_data=appointment_data, auto_confirm=True, ignore_limits=ignore_limits)

    email_tasks.add_task(appointment.send_confirmation_email)

    return appointment


@appointments.patch("/appointments/{appointment_id}/confirm")
async def confirm_appointment(
        appointment_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.confirm_appointment(db=db, appointment_id=appointment_id)

    email_tasks.add_task(appointment.send_confirmation_email)

    return appointment


@appointments.patch("/appointments/{appointment_id}/cancel")
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


@appointments.post("/appointments/types")
async def create_appointment_type(new_appointment_type: schemas.AppointmentType, db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    return crud.create_appointment_type(db=db, appointment_type_data=new_appointment_type)


@appointments.patch("/appointments/types/{type_id}")
async def update_appointment_type(
        type_id: str,
        updated_appointment_type_data: schemas.PatchAppointmentType,
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    appointment_type = crud.get_appointment_type(db=db, appointment_type_id=type_id)
    return crud.update_appointment_type(db=db, appointment_type=appointment_type, updated_appointment_type_data=updated_appointment_type_data)


@appointments.get("/appointments/calendar")
async def get_appointments(
        start_datetime: datetime = datetime.utcnow(),
        end_datetime: datetime = datetime.utcnow() + relativedelta.relativedelta(weeks=1),
        db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentFull]:
    booked_appointments = crud.get_appointments(db=db, start_datetime=start_datetime, end_datetime=end_datetime)

    return booked_appointments
