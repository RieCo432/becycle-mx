import datetime
import math
from copy import copy

from sqlalchemy import and_
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from .settings import *
from uuid import UUID


def create_appointment(db: Session, appointment_data: schemas.AppointmentCreate, auto_confirm: bool = False) -> models.Appointment:
    # auto_confirm can be used if appointment is created by staff directly
    appointment_type = get_appointment_type(db=db, appointment_type_id=appointment_data.typeId)

    required_consecutive_slots = math.ceil(appointment_type.duration / get_slot_duration(db=db))

    if not are_consecutive_slots_available_on_datetime(db=db, n_slots=required_consecutive_slots, dt=appointment_data.startDateTime):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "There are not enough free slots for this appointment"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    appointment = models.Appointment(
        clientId=appointment_data.clientId,
        typeId=appointment_data.typeId,
        startDateTime=appointment_data.startDateTime,
        endDateTime=appointment_data.startDateTime + relativedelta(minutes=appointment_type.duration),
        notes=appointment_data.notes,
        confirmed=auto_confirm
    )

    db.add(appointment)
    db.commit()

    return appointment


def get_appointment(db: Session, appointment_id: UUID) -> models.Appointment:
    appointment = db.scalar(
        select(models.Appointment)
        .where(models.Appointment.id == appointment_id)
    )

    return appointment


def confirm_appointment(db: Session, appointment_id: UUID) -> models.Appointment:
    appointment = get_appointment(db=db, appointment_id=appointment_id)

    appointment.confirmed = True

    db.commit()

    return appointment


def cancel_appointment(db: Session, appointment_id: UUID) -> models.Appointment:
    appointment = get_appointment(db=db, appointment_id=appointment_id)

    appointment.cancelled = True

    db.commit()

    return appointment


def get_appointments_by_datetime(db: Session, dt: datetime) -> list[models.Appointment]:
    return [_ for _ in db.scalars(
        select(models.Appointment)
        .where(
            (models.Appointment.startDateTime <= dt)
            & (models.Appointment.endDateTime > dt)
            & (models.Appointment.cancelled == False)
        )
    )]


def get_remaining_concurrent_appointments_for_each_slot(db: Session) -> dict[date, dict[time, int]]:
    maximum_concurrent_appointments_for_each_slot = get_maximum_concurrent_appointments_for_each_slot(db=db)

    remaining_concurrent_appointments_for_each_slot = {}

    for d in maximum_concurrent_appointments_for_each_slot.keys():
        remaining_concurrent_appointments_for_each_slot[d] = {}
        for t in maximum_concurrent_appointments_for_each_slot[d].keys():
            # for each 15-minute slot get the non-cancelled appointments that will be happening at that date and time
            appointments_on_slot = get_appointments_by_datetime(db=db, dt=datetime.combine(d, t))
            # subtract the number of booked appointments from the maximum number of concurrent appointments
            remaining_concurrent_appointments_for_each_slot[d][t] = (maximum_concurrent_appointments_for_each_slot[d][t]
                                                                     - len(appointments_on_slot))

    return remaining_concurrent_appointments_for_each_slot


def are_consecutive_slots_available_on_datetime(db: Session, n_slots: int, dt: datetime, remaining_concurrent_appointments_for_each_slot: dict[date, dict[time, int]] | None = None) -> bool:
    # if called as part of regular availability query, this dict can be passed in order to save time on not having to compute it again
    # but at the moment that the appointment is recorded, availability should be re-checked, so in that case this method
    # has to load the availability from scratch
    if remaining_concurrent_appointments_for_each_slot is None:
        remaining_concurrent_appointments_for_each_slot = get_remaining_concurrent_appointments_for_each_slot(db=db)

    slot_duration = get_slot_duration(db=db)

    # starting at dt + 0, check if the remaining number of slots available for each consecutive slot is higher than 0
    # up to n_slots (excluded).
    # For a single slot, this will only check the datetime that was passed.
    # For two slots, it will check the passed datetime, and the next one
    # For three slots, it will check the passed datetime and the next two, ...
    # If any of the checked slots have no availability, return False
    for i_slot in range(n_slots):
        i_slot_datetime = dt + relativedelta(minutes=i_slot * slot_duration)
        # using .get() instead of [] ensures we can return a default value of [] times or 0 remaining slots in case of
        # missing entries
        if (remaining_concurrent_appointments_for_each_slot
                .get(i_slot_datetime.date(), {})
                .get(i_slot_datetime.time(), 0) == 0):
            return False

    # this point can only be reached if enough consecutive slots have availability
    return True


def get_available_start_dates_and_times_for_appointment_type(db: Session, appointment_type_id: str) -> dict[date, list[time]]:
    appointment_type = get_appointment_type(db=db, appointment_type_id=appointment_type_id)

    required_consecutive_slots = math.ceil(appointment_type.duration / get_slot_duration(db=db))

    remaining_concurrent_appointments_for_each_slot = get_remaining_concurrent_appointments_for_each_slot(db=db)

    # hold every time slot that the appointment could start on, grouped by date
    available_appointment_start_dates_and_times: dict[date, list[time]] = {}

    # for every slot in the remaining availability, query whether enough consecutive slots are available
    for d in remaining_concurrent_appointments_for_each_slot.keys():
        for t in remaining_concurrent_appointments_for_each_slot[d].keys():
            if are_consecutive_slots_available_on_datetime(db=db, n_slots=required_consecutive_slots,
                                                           dt=datetime.combine(d, t),
                                                           remaining_concurrent_appointments_for_each_slot=
                                                           remaining_concurrent_appointments_for_each_slot):
                if d not in available_appointment_start_dates_and_times:
                    available_appointment_start_dates_and_times[d] = [t]
                else:
                    available_appointment_start_dates_and_times[d].append(t)

    return available_appointment_start_dates_and_times


def get_appointment_types(db: Session, inactive: bool) -> list[models.AppointmentType]:
    return [_ for _ in db.scalars(
        select(models.AppointmentType)
        .where(models.AppointmentType.active | inactive)
    )]


def get_appointments(db: Session, start_datetime: datetime = None, end_datetime: datetime = None, client_id: UUID = None) -> list[models.Appointment]:
    query_filter = []
    if client_id is not None:
        query_filter.append((models.Appointment.clientId == client_id))
    if start_datetime is not None:
        query_filter.append((models.Appointment.startDateTime >= start_datetime))
    if end_datetime is not None:
        query_filter.append((models.Appointment.endDateTime <= end_datetime))
    return [_ for _ in db.scalars(
        select(models.Appointment)
        .where(and_(*query_filter))
    )]


def update_appointment_type(db: Session, appointment_type: models.AppointmentType, updated_appointment_type_data: schemas.PatchAppointmentType) -> models.AppointmentType:
    if updated_appointment_type_data.duration is not None:
        appointment_type.duration = updated_appointment_type_data.duration
    if updated_appointment_type_data.title is not None:
        appointment_type.title = updated_appointment_type_data.title
    if updated_appointment_type_data.active is not None:
        appointment_type.active = updated_appointment_type_data.active
    if updated_appointment_type_data.description is not None:
        appointment_type.description = updated_appointment_type_data.description

    db.commit()

    return appointment_type


def create_appointment_type(db: Session, appointment_type_data: schemas.AppointmentType) -> models.AppointmentType:
    new_appointment_type = models.AppointmentType(
        id=appointment_type_data.id,
        title=appointment_type_data.title,
        description=appointment_type_data.description,
        duration=appointment_type_data.duration,
        active=appointment_type_data.active
    )

    try:
        db.add(new_appointment_type)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This appointment type ID already exists!"})

    return new_appointment_type
