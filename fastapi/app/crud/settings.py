import math
from copy import copy
from datetime import date, datetime, time, timedelta
from uuid import UUID

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
    if updated_appointment_settings.gradualAvailability is not None:
        appointment_general_settings.gradualAvailability = updated_appointment_settings.gradualAvailability

    db.commit()
    return appointment_general_settings


def get_appointment_concurrency_limits(db: Session, weekday: int | None = None) -> list[models.AppointmentConcurrencyLimit]:
    appointment_concurrency_limits_query = (select(models.AppointmentConcurrencyLimit)
                                            .order_by(models.AppointmentConcurrencyLimit.weekDay)
                                            .order_by(models.AppointmentConcurrencyLimit.afterTime))

    if weekday is not None:
        appointment_concurrency_limits_query = appointment_concurrency_limits_query.where(models.AppointmentConcurrencyLimit.weekDay == weekday)

    appointment_concurrency_limits = [_ for _ in db.scalars(appointment_concurrency_limits_query)]

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

    opening_days = get_opening_week_days(db=db)

    if appointment_concurrency_limit_data.weekDay not in opening_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "The specified weekday is not in the list of opening days."}
        )

    new_appointment_concurrency_limit = models.AppointmentConcurrencyLimit(
        weekDay=appointment_concurrency_limit_data.weekDay,
        afterTime=appointment_concurrency_limit_data.afterTime,
        maxConcurrent=appointment_concurrency_limit_data.maxConcurrent
    )

    try:
        db.add(new_appointment_concurrency_limit)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "There already is a concurrency limit for this time and weekday!"})

    return new_appointment_concurrency_limit


def patch_appointment_concurrency_limit(
        db: Session,
        weekday: int,
        after_time: time,
        new_appointment_concurrency_limit_data: schemas.PatchAppointmentConcurrencyLimit) -> models.AppointmentConcurrencyLimit:

    appointment_concurrency_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(
            (models.AppointmentConcurrencyLimit.afterTime == after_time)
            & (models.AppointmentConcurrencyLimit.weekDay == weekday)
        )
    )

    if appointment_concurrency_limit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "There is no limit for this time or weekday!"})

    if new_appointment_concurrency_limit_data.weekDay is not None:
        if new_appointment_concurrency_limit_data.weekDay not in get_opening_week_days(db=db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"description": "The specified weekday is not in the list of opening days."}
            )
        appointment_concurrency_limit.weekDay = new_appointment_concurrency_limit_data.weekDay
    if new_appointment_concurrency_limit_data.afterTime is not None:
        appointment_concurrency_limit.afterTime = new_appointment_concurrency_limit_data.afterTime
    if new_appointment_concurrency_limit_data.maxConcurrent is not None:
        appointment_concurrency_limit.maxConcurrent = new_appointment_concurrency_limit_data.maxConcurrent

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Is there already a limit for this time or weekday?"})

    return appointment_concurrency_limit


def delete_appointment_concurrency_limit(
        db: Session,
        weekday: int,
        after_time: time) -> None:

    appointment_concurrency_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(
            (models.AppointmentConcurrencyLimit.afterTime == after_time)
            & (models.AppointmentConcurrencyLimit.weekDay == weekday)
        )
    )

    if appointment_concurrency_limit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "This appointment concurrency limit does not exist!"})

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


def get_theoretical_open_days_in_period(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[date]:
    period_start = start_date if start_date is not None else datetime.utcnow().date()
    period_end = end_date if end_date is not None else datetime.utcnow().date() + relativedelta(months=6)

    opening_weekdays = get_opening_week_days(db=db)

    theoretical_open_days = [d.date() for d in rrule(DAILY, dtstart=period_start, until=period_end)
                             if (d.weekday() in opening_weekdays)]

    return theoretical_open_days


def get_open_days_in_period(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[date]:
    if start_date is None:
        start_date = datetime.utcnow().date()
    if end_date is None:
        end_date = (datetime.utcnow() + relativedelta(months=6)).date()

    theoretical_open_days = get_theoretical_open_days_in_period(db=db, start_date=start_date, end_date=end_date)
    closed_dates = [closedDay.date for closedDay in get_closed_days(db=db, start_date=start_date, end_date=end_date)]

    open_days = [d for d in theoretical_open_days if d not in closed_dates]

    return open_days


def get_upcoming_closures(db:Session, start_date: date | None = None, end_date: date | None = None) -> list[schemas.Closure]:
    query = select(models.ClosedDay)

    if start_date is not None:
        query = query.where(models.ClosedDay.date >= start_date)

    closed_days = [_ for _ in db.scalars(query)]
    closed_days_dates = [closed_day.date for closed_day in closed_days]


    theoretical_open_dates = get_theoretical_open_days_in_period(db=db, start_date=start_date, end_date=end_date)
    upcoming_closures = []

    probe = 0

    while probe < len(theoretical_open_dates)-1:
        if theoretical_open_dates[probe] in closed_days_dates:
            probe_ahead = probe + 1
            while theoretical_open_dates[probe_ahead] in closed_days_dates:
                probe_ahead += 1

            if probe_ahead == probe + 1:
                upcoming_closures.append(schemas.Closure(
                    type="day",
                    item=schemas.ClosedDay(
                        date=theoretical_open_dates[probe],
                        note=db.scalar(select(models.ClosedDay.note).where(
                            models.ClosedDay.date == theoretical_open_dates[probe])),
                    )
                ))
            else:
                upcoming_closures.append(schemas.Closure(
                    type="period",
                    item=schemas.ClosedPeriod(
                        date=theoretical_open_dates[probe],
                        untilDate=theoretical_open_dates[probe_ahead - 1],
                        nextOpen=theoretical_open_dates[probe_ahead],
                        note=db.scalar(select(models.ClosedDay.note).where(
                            models.ClosedDay.date == theoretical_open_dates[probe])),
                    )
                ))
            probe = probe_ahead
        else:
            probe += 1

    return upcoming_closures


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

def get_gradual_availability(db: Session) -> bool:
    return db.scalar(
        select(models.AppointmentGeneralSettings.gradualAvailability)
    )


def get_calendar_time_range(db: Session) -> dict[str, time]:
    open_time = db.scalar(
        select(models.AppointmentConcurrencyLimit.afterTime)
        .where(models.AppointmentConcurrencyLimit.maxConcurrent > 0)
        .order_by(models.AppointmentConcurrencyLimit.afterTime)
    )
    close_time = db.scalar(
        select(models.AppointmentConcurrencyLimit.afterTime)
        .where(
            models.AppointmentConcurrencyLimit.maxConcurrent == 0
        )
        .order_by(models.AppointmentConcurrencyLimit.afterTime.desc())
    )

    return {
        "open_time": open_time,
        "close_time": close_time,
    }


def get_slot_duration(db: Session) -> int:
    return db.scalar(
        select(models.AppointmentGeneralSettings.slotDuration)
    )


def get_open_days_in_booking_period(db: Session) -> list[date]:
    period_start = datetime.utcnow().date() + relativedelta(days=get_min_book_ahead(db=db))
    period_end = datetime.utcnow().date() + relativedelta(days=get_max_book_ahead(db=db))

    closed_dates = [closed_day.date for closed_day in get_closed_days(db=db, start_date=period_start)]

    theoretical_open_days = get_theoretical_open_days_in_period(db=db, start_date=period_start, end_date=period_end)

    actual_open_days = [day for day in theoretical_open_days if day not in closed_dates]

    return actual_open_days


def get_maximum_concurrent_appointments_for_each_slot_of_weekday(db: Session, weekday: int) -> dict[time, int]:
    appointment_concurrency_limits_by_time_after = {acl.afterTime: acl.maxConcurrent for acl in get_appointment_concurrency_limits(db=db, weekday=weekday)}

    if len(appointment_concurrency_limits_by_time_after) == 0:
        return {}

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
    maximum_concurrent_appointments_for_each_slot = {}

    opening_days_in_booking_period = get_open_days_in_booking_period(db=db)
    for opening_date in opening_days_in_booking_period:
        maximum_concurrent_appointments_for_each_slot[opening_date] = get_maximum_concurrent_appointments_for_each_slot_of_weekday(db=db, weekday=opening_date.weekday())

    return maximum_concurrent_appointments_for_each_slot


def get_maximum_concurrent_appointments_for_each_slot_adjusted_for_time_until_appointment(db: Session) -> dict[date, dict[time, int]]:
    maximum_concurrent_appointments_for_each_slot = get_maximum_concurrent_appointments_for_each_slot(db=db)

    maximum_concurrent_appointments_for_each_slot_adjusted_for_time_until_appointment = {}

    min_book_ahead = get_min_book_ahead(db=db)
    max_book_ahead = get_max_book_ahead(db=db)

    for d in maximum_concurrent_appointments_for_each_slot.keys():
        maximum_concurrent_appointments_for_each_slot_adjusted_for_time_until_appointment[d] = {}
        days_from_today = (d - datetime.utcnow().date()).days - 1  # we don't want to live right on the edge

        adjustment_factor = min((max_book_ahead - days_from_today) / (max_book_ahead - min_book_ahead), 1) if get_gradual_availability(db=db) else 1

        for t in maximum_concurrent_appointments_for_each_slot[d].keys():
            maximum_concurrent_appointments_for_each_slot_adjusted_for_time_until_appointment[d][t] = (math.ceil(
                    adjustment_factor * maximum_concurrent_appointments_for_each_slot[d][t]))

    return maximum_concurrent_appointments_for_each_slot_adjusted_for_time_until_appointment


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

    day_translate = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    opening_times = []

    for opening_weekday in general_settings.openingDays:
        appointment_concurrency_limits = get_appointment_concurrency_limits(db=db, weekday=opening_weekday)
        open_time = None
        close_time = None
        for appointment_concurrency_limit in appointment_concurrency_limits:
            if open_time is None and appointment_concurrency_limit.maxConcurrent > 0:
                open_time = appointment_concurrency_limit.afterTime

            if appointment_concurrency_limit.maxConcurrent == 0:
                close_time = appointment_concurrency_limit.afterTime

            if open_time is not None and close_time is not None and close_time > open_time:
                break

        if open_time is not None and close_time is not None:
            opening_times.append(
                schemas.DayOpeningTimes(
                    day=day_translate[opening_weekday],
                    open="{:02d}:{:02d}".format(open_time.hour, open_time.minute),
                    close="{:02d}:{:02d}".format(close_time.hour, close_time.minute),
                )
            )

    return opening_times


def get_about_us(db: Session) -> models.AboutUs:
    return db.scalar(
        select(models.AboutUs)
        .where(models.AboutUs.id == 1)
    )


def set_about_us_html(db: Session, new_about_us: schemas.AboutUs) -> models.AboutUs:
    about_us = get_about_us(db=db)

    about_us.html = new_about_us.html
    db.commit()

    return about_us


def get_active_faq(db: Session) -> list[models.Faq]:
    return [_ for _ in db.scalars(
        select(models.Faq)
        .where(models.Faq.active == True))
            ]

def get_all_faq(db: Session) -> list[models.Faq]:
    return [_ for _ in db.scalars(
        select(models.Faq)
    )]

def get_faq(db: Session, faq_id: UUID) -> models.Faq:
    return db.scalar(
        select(models.Faq)
        .where(models.Faq.id == faq_id)
    )

def update_faq(db: Session, faq_id: UUID, updated_faq: schemas.UpdateFaq) -> models.Faq:
    faq = get_faq(db=db, faq_id=faq_id)

    if faq is not None:
        faq.question = updated_faq.question
        faq.answer = updated_faq.answer
        faq.active = updated_faq.active

    db.commit()

    return faq

def create_faq(db: Session, new_faq: schemas.FaqBase) -> schemas.Faq:
    faq = models.Faq(
        question=new_faq.question,
        answer=new_faq.answer,
        active=True,
    )
    db.add(faq)
    db.commit()
    return faq


def swap_faq_order(db: Session, faq1_id: UUID, faq2_id: UUID) -> list[models.Faq]:
    faq1 = get_faq(db=db, faq_id=faq1_id)
    faq2 = get_faq(db=db, faq_id=faq2_id)

    faq1_old_order_index = faq1.orderIndex
    faq2_old_order_index = faq2.orderIndex

    try:
        faq2.orderIndex = -1
        db.commit()
        faq1.orderIndex = faq2_old_order_index
        db.commit()
        faq2.orderIndex = faq1_old_order_index
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": str(e)})

    return [faq1, faq2]