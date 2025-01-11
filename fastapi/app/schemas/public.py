from pydantic import BaseModel
from datetime import date
from .settings import ClosedDay


class DayOpeningTimes(BaseModel):
    day: str
    open: str
    close: str


class ClosedPeriod(ClosedDay):
    untilDate: date
    nextOpen: date


class ClosedEntry(BaseModel):
    type: str
    item: ClosedDay | ClosedPeriod
