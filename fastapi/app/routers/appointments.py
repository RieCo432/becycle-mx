from datetime import datetime
from typing import Annotated
from uuid import UUID
from dateutil import relativedelta
from fastapi import APIRouter, Depends, BackgroundTasks, Body, HTTPException
from sqlalchemy.orm import Session
from starlette import status

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
        cancellation_detail: schemas.AppointmentCancellationDetail,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    appointment = crud.cancel_appointment(db=db, appointment_id=appointment_id, cancellation_detail=cancellation_detail)

    if appointment.confirmed:
        email_tasks.add_task(appointment.send_cancellation_email)
    else:
        email_tasks.add_task(appointment.send_request_denied_email)

    return appointment


@appointments.post("/appointments/types")
async def create_appointment_type(new_appointment_type: schemas.AppointmentTypeCreate, db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    return crud.create_appointment_type(db=db, appointment_type_data=new_appointment_type)


@appointments.patch("/settings/appointments/swap")
async def patch_swap_faq(
        appointment_type_1_id: Annotated[str, Body(embed=True)],
        appointment_type_2_id: Annotated[str, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> list[schemas.AppointmentType]:
    if crud.get_appointment_type(db=db, appointment_type_id=appointment_type_1_id) is None or crud.get_appointment_type(db=db, appointment_type_id=appointment_type_2_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more Appointment Types not found."})

    return crud.swap_appointment_type_order(db=db, type1_id=appointment_type_1_id, type2_id=appointment_type_2_id)


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
