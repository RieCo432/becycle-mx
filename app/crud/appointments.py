import math
from copy import copy

from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from .settings import *
from uuid import UUID
from .settings import get_closed_dates_after_date, get_min_book_ahead, get_max_book_ahead, get_opening_week_days


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


def get_open_days(db: Session) -> list[date]:
    period_start = datetime.utcnow().date() + relativedelta(days=get_min_book_ahead(db=db))
    period_end = datetime.utcnow().date() + relativedelta(days=get_max_book_ahead(db=db))

    closed_dates = get_closed_dates_after_date(db=db, after_date=period_start)

    opening_weekdays = get_opening_week_days(db=db)

    open_days = [d.date() for d in rrule(DAILY, dtstart=period_start, until=period_end)
                 if (d.weekday() in opening_weekdays)
                 and d.date() not in closed_dates]

    return open_days


def get_maximum_concurrent_appointments_for_each_slot_of_day(db: Session) -> dict[time, int]:
    appointment_concurrency_limits_by_time_after = {acl.afterTime: acl.maxConcurrent for acl in get_appointment_concurrency_limits(db=db)}
    sorted_appointment_concurrency_limit_times = sorted(appointment_concurrency_limits_by_time_after.keys())

    slot_duration = get_slot_duration(db=db)

    maximum_concurrent_appointments_for_each_slot_of_day = {}
    # get the first time that has a limit higher than 0
    # this avoids iterating over all the 15-minute slots between midnight and the first slot with a non 0 limit
    t = next(t for t in sorted_appointment_concurrency_limit_times if appointment_concurrency_limits_by_time_after[t] > 0)

    # manually add a limit of 0 for 15 minutes before the first non-zero slot
    # this has no functional role, but might add a bit of visual padding to the resulting table
    maximum_concurrent_appointments_for_each_slot_of_day[
        (datetime.combine(date(year=1, month=1, day=1), t) - relativedelta(minutes=slot_duration)).time()
    ] = 0

    active_concurrency_limit = appointment_concurrency_limits_by_time_after[t]
    while t <= time(hour=23, minute=59):
        maximum_concurrent_appointments_for_each_slot_of_day[t] = active_concurrency_limit

        # if we have reached the last concurrency rule and the limit is 0, exit the loop
        if t == sorted_appointment_concurrency_limit_times[-1] and active_concurrency_limit == 0:
            break

        # to add 15 minutes to a time object, we create a full datetime object using 01/01/01 as a date
        # add 15 minutes relativedelta and then get only the time of the resulting datetime object
        t = (datetime.combine(date(year=1, month=1, day=1), t) + relativedelta(minutes=slot_duration)).time()
        active_concurrency_limit = appointment_concurrency_limits_by_time_after.get(t, active_concurrency_limit)

    return maximum_concurrent_appointments_for_each_slot_of_day


def get_maximum_concurrent_appointments_for_each_slot(db: Session) -> dict[date, dict[time, int]]:
    maximum_concurrent_appointments_for_each_slot_of_day = get_maximum_concurrent_appointments_for_each_slot_of_day(db=db)

    maximum_concurrent_appointments_for_each_slot = {
        d: copy(maximum_concurrent_appointments_for_each_slot_of_day)
        for d in get_open_days(db=db)
    }

    return maximum_concurrent_appointments_for_each_slot


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
