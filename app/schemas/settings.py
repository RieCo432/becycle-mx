from datetime import time, date

from pydantic import BaseModel


class AppointmentType(BaseModel):
    id: str
    active: bool
    title: str
    description: str
    duration: int


class PatchAppointmentType(BaseModel):
    active: bool | None = None
    title: str | None = None
    description: str | None = None
    duration: int | None = None


class AppointmentGeneralSettings(BaseModel):
    openingDays: list[int]
    minBookAhead: int
    maxBookAhead: int
    slotDuration: int


class PatchAppointmentGeneralSettings(BaseModel):
    openingDays: list[int] | None = None
    minBookAhead: int | None = None
    maxBookAhead: int | None = None
    slotDuration: int | None = None


class AppointmentConcurrencyLimit(BaseModel):
    afterTime: time
    maxConcurrent: int


class PatchAppointmentConcurrencyLimit(BaseModel):
    afterTime: time | None = None
    maxConcurrent: int | None = None


class ClosedDay(BaseModel):
    date: date
    note: str
