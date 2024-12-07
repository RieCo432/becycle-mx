from copy import copy
from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_appointment_general_settings(db: Session) -> models.AppointmentGeneralSettings:
    appointment_general_settings = db.scalar(
        select(models.AppointmentGeneralSettings)
        .where(models.AppointmentGeneralSettings.id == 1)
    )

    return appointment_general_settings


def update_appointment_general_settings(db: Session, updated_appointment_settings: schemas.PatchAppointmentGeneralSettings) -> models.AppointmentGeneralSettings:
    appointment_general_settings = get_appointment_general_settings(db=db)

    if updated_appointment_settings.openingDays is not None:
        appointment_general_settings.openingDays = updated_appointment_settings.openingDays
    if updated_appointment_settings.minBookAhead is not None:
        appointment_general_settings.minBookAhead = updated_appointment_settings.minBookAhead
    if updated_appointment_settings.maxBookAhead is not None:
        appointment_general_settings.maxBookAhead = updated_appointment_settings.maxBookAhead
    if updated_appointment_settings.slotDuration is not None:
        appointment_general_settings.slotDuration = updated_appointment_settings.slotDuration

    db.commit()
    return appointment_general_settings


def get_appointment_concurrency_limits(db: Session) -> list[models.AppointmentConcurrencyLimit]:
    appointment_concurrency_limits = [_ for _ in db.scalars(
        select(models.AppointmentConcurrencyLimit)
        .order_by(models.AppointmentConcurrencyLimit.afterTime)
    )]

    return appointment_concurrency_limits


def get_appointment_type(db: Session, appointment_type_id: str) -> models.AppointmentType:
    appointment_type = db.scalar(
        select(models.AppointmentType)
        .where(models.AppointmentType.id == appointment_type_id)
    )

    return appointment_type


def add_appointment_concurrency_limit(
        db: Session,
        appointment_concurrency_limit_data: schemas.AppointmentConcurrencyLimit) -> models.AppointmentConcurrencyLimit:

    new_appointment_concurrency_limit = models.AppointmentConcurrencyLimit(
        afterTime=appointment_concurrency_limit_data.afterTime,
        maxConcurrent=appointment_concurrency_limit_data.maxConcurrent
    )

    try:
        db.add(new_appointment_concurrency_limit)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "There already is a concurrency limit for this time!"})

    return new_appointment_concurrency_limit


def patch_appointment_concurrency_limit(
        db: Session,
        after_time: time,
        new_appointment_concurrency_limit_data: schemas.PatchAppointmentConcurrencyLimit) -> models.AppointmentConcurrencyLimit:

    appointment_concurrency_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == after_time)
    )

    if appointment_concurrency_limit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "There is no limit for this time!"})

    if new_appointment_concurrency_limit_data.afterTime is not None:
        appointment_concurrency_limit.afterTime = new_appointment_concurrency_limit_data.afterTime
    if new_appointment_concurrency_limit_data.maxConcurrent is not None:
        appointment_concurrency_limit.maxConcurrent = new_appointment_concurrency_limit_data.maxConcurrent

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Is there already a limit for this time?"})

    return appointment_concurrency_limit


def delete_appointment_concurrency_limit(
        db: Session,
        after_time: time) -> None:

    appointment_concurrency_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == after_time)
    )

    if appointment_concurrency_limit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "This appointment concurrency does not exist!"})

    db.delete(appointment_concurrency_limit)
    db.commit()


def get_closed_day(db: Session, closed_day_date: date) -> models.ClosedDay:
    closed_day = db.scalar(
        select(models.ClosedDay)
        .where(models.ClosedDay.date == closed_day_date)
    )

    if closed_day is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This date is not registered as a closed day."})

    return closed_day


def get_closed_days(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[models.ClosedDay]:
    query_filter = []
    if start_date is not None:
        query_filter.append(models.ClosedDay.date >= start_date)
    if end_date is not None:
        query_filter.append(models.ClosedDay.date <= end_date)
    return [_ for _ in db.scalars(
        select(models.ClosedDay)
        .where(
            and_(*query_filter)
        )
        .order_by(models.ClosedDay.date)
    )]


def create_closed_day(
        db: Session,
        closed_day_data: schemas.ClosedDay) -> models.ClosedDay:

    closed_day = models.ClosedDay(
        date=closed_day_data.date,
        note=closed_day_data.note
    )

    try:
        db.add(closed_day)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This day is already closed."})

    return closed_day


def delete_closed_day(
        db: Session,
        closed_day_date: date) -> None:
    closed_day = get_closed_day(db=db, closed_day_date=closed_day_date)

    db.delete(closed_day)
    db.commit()


def get_min_book_ahead(db: Session) -> int:
    return db.scalar(
        select(models.AppointmentGeneralSettings.minBookAhead)
    )


def get_max_book_ahead(db: Session) -> int:
    return db.scalar(
        select(models.AppointmentGeneralSettings.maxBookAhead)
    )


def get_opening_week_days(db: Session) -> list[int]:
    return db.scalar(
        select(models.AppointmentGeneralSettings.openingDays)
    )


def get_opening_hours(db: Session) -> dict[str, time]:
    open_time = db.scalar(
        select(models.AppointmentConcurrencyLimit.afterTime)
        .where(models.AppointmentConcurrencyLimit.maxConcurrent > 0)
        .order_by(models.AppointmentConcurrencyLimit.afterTime)
    )
    close_time = db.scalar(
        select(models.AppointmentConcurrencyLimit.afterTime)
        .where(
            (models.AppointmentConcurrencyLimit.afterTime > open_time)
            & (models.AppointmentConcurrencyLimit.maxConcurrent == 0)
        )
        .order_by(models.AppointmentConcurrencyLimit.afterTime)
    )

    return {
        "open_time": open_time,
        "close_time": close_time,
    }


def get_slot_duration(db: Session) -> int:
    return db.scalar(
        select(models.AppointmentGeneralSettings.slotDuration)
    )


def get_open_days(db: Session) -> list[date]:
    period_start = datetime.utcnow().date() + relativedelta(days=get_min_book_ahead(db=db))
    period_end = datetime.utcnow().date() + relativedelta(days=get_max_book_ahead(db=db))

    closed_dates = [closed_day.date for closed_day in get_closed_days(db=db, start_date=period_start)]

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


def get_address(db: Session) -> models.Address:
    return db.scalar(
        select(models.Address)
        .where(models.Address.id == 1)
    )


def update_address(db: Session, new_address: schemas.Address) -> models.Address:
    current_address = get_address(db=db)

    current_address.number = new_address.number
    current_address.street = new_address.street
    current_address.postcode = new_address.postcode
    current_address.city = new_address.city

    db.commit()

    return current_address


def get_expense_types(db: Session) -> list[models.ExpenseType]:
    return [
        _ for _ in db.scalars(
            select(models.ExpenseType)
        )
    ]


def get_contract_types(db: Session) -> list[models.ContractType]:
    return [
        _ for _ in db.scalars(
            select(models.ContractType)
        )
    ]


def add_contract_type(db: Session, new_contract_type: schemas.ContractType) -> models.ContractType:
    contract_type = models.ContractType(
        id=new_contract_type.id
    )

    try:
        db.add(contract_type)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This contract type already exists!"})
    return contract_type


def delete_contract_type(db: Session, contract_type_id: str) -> models.ContractType:
    contract_type = db.scalar(
        select(models.ContractType)
        .where(models.ContractType.id == contract_type_id)
    )

    db.delete(contract_type)
    db.commit()
    return contract_type


def add_expense_type(db: Session, new_expense_type: schemas.ExpenseType) -> models.ExpenseType:
    expense_type = models.ExpenseType(
        id=new_expense_type.id,
        description=new_expense_type.description
    )

    try:
        db.add(expense_type)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This expense type already exists!"})

    return expense_type


def delete_expense_type(db: Session, expense_type_id: str) -> models.ExpenseType:
    expense_type = db.scalar(
        select(models.ExpenseType)
        .where(models.ExpenseType.id == expense_type_id)
    )
    db.delete(expense_type)
    db.commit()
    return expense_type


def update_expense_type(db: Session, expense_type_id: str, description: str) -> models.ExpenseType:
    expense_type = db.scalar(
        select(models.ExpenseType)
        .where(models.ExpenseType.id == expense_type_id)
    )

    expense_type.description = description
    db.commit()
    return expense_type


def get_opening_times(db: Session) -> list[schemas.DayOpeningTimes]:
    general_settings = get_appointment_general_settings(db=db)
    appointment_concurrency_limits = get_appointment_concurrency_limits(db=db)

    day_translate = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    opening_times = []

    for opening_weekday in general_settings.openingDays:
        open_time = None
        close_time = None
        for appointment_concurrency_limit in appointment_concurrency_limits:
            if open_time is None and appointment_concurrency_limit.maxConcurrent > 0:
                open_time = appointment_concurrency_limit.afterTime

            if appointment_concurrency_limit.maxConcurrent == 0:
                close_time = appointment_concurrency_limit.afterTime

            if open_time is not None and close_time is not None and close_time > open_time:
                break

        opening_times.append(
            schemas.DayOpeningTimes(
                day=day_translate[opening_weekday],
                open="{:02d}:{:02d}".format(open_time.hour, open_time.minute),
                close="{:02d}:{:02d}".format(close_time.hour, close_time.minute),
            )
        )

    return opening_times
