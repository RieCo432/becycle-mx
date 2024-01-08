from sqlalchemy.orm import Session
import app.schemas as schemas
from .settings import get_appointment_general_settings, get_appointment_concurrency_limits


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

