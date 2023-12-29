from pydantic import BaseModel
from datetime import time, date


class AppointmentType(BaseModel):
    id: str
    active: bool
    title: str
    description: str
    duration: int


class AppointmentGeneralSettings(BaseModel):
    openingDays: list[int]
    minBookAhead: int
    maxBookAhead: int
    slotDuration: int


class AppointmentConcurrencyLimit(BaseModel):
    afterTime: time
    maxConcurrent: int


class ClosedDay(BaseModel):
    date: date
    note: str
