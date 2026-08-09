from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

appointments_public = APIRouter(
    tags=["appointments-public"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)

@appointments_public.get("/public/appointments")
async def get_appointment_via_hyperlink(
        appointment_id: UUID,
        client_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.AppointmentFull:
    crud.verify_appointment_hyperlink_parameters(db=db, appointment_id=appointment_id, client_id=client_id)
    return crud.get_appointment(db=db, appointment_id=appointment_id)


@appointments_public.patch("/public/appointments/cancel")
async def cancel_appointment_via_hyperlink(
        appointment_id: UUID,
        client_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.verify_appointment_hyperlink_parameters(db=db, appointment_id=appointment_id, client_id=client_id)
    appointment = crud.cancel_appointment(db=db, appointment_id=appointment_id, cancellation_detail=schemas.AppointmentCancellationDetail(
        reason="Cancelled via hyperlink"
    ))

    email_tasks.add_task(appointment.send_client_cancellation_email)
    
    
@appointments_public.patch("/public/appointment/reschedule")
async def reschedule_via_hyperlink(
        appointment_id: UUID,
        client_id: UUID,
        new_appointment_info: schemas.AppointmentReschedule,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)
) -> None:
    print("reschedule_via_hyperlink")
    crud.verify_appointment_hyperlink_parameters(db=db, appointment_id=appointment_id, client_id=client_id)
    
    appointment_to_reschedule = crud.get_appointment(db=db, appointment_id=appointment_id)
    
    appointment = crud.reschedule_appointment(db=db, reschedule_appointment_id=appointment_id, appointment_data=new_appointment_info, auto_confirm=False, ignore_limits=False)
    email_tasks.add_task(appointment.send_rescheduled_email(appointment_to_reschedule))



@appointments_public.get("/public/appointments/available")
async def get_available_appointments(
        appointment_type_id: str,
        ignore_limits: bool = False,
        db: Session = Depends(dep.get_db)) -> dict[date, list[dict]]:
    if ignore_limits:
        Depends(dep.get_current_appointment_manager_user)
    available_slots = crud.get_available_start_dates_and_times_for_appointment_type(db=db, appointment_type_id=appointment_type_id, ignore_limits=ignore_limits)

    return available_slots


@appointments_public.get("/public/appointments/types")
async def get_appointment_types(inactive: bool = False, db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentType]:
    return crud.get_appointment_types(db=db, inactive=inactive)


@appointments_public.get("/public/appointments/types/{type_id}")
async def get_appointment_type(type_id: str, db: Session = Depends(dep.get_db)) -> schemas.AppointmentType:
    return crud.get_appointment_type(db=db, appointment_type_id=type_id)