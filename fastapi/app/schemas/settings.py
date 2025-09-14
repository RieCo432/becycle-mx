from datetime import time, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class AppointmentTypeCreate(BaseModel):
    id: str
    active: bool
    title: str
    description: str
    duration: int

class AppointmentType(AppointmentTypeCreate):
    orderIndex: int


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
    gradualAvailability: bool


class PatchAppointmentGeneralSettings(BaseModel):
    openingDays: list[int] | None = None
    minBookAhead: int | None = None
    maxBookAhead: int | None = None
    slotDuration: int | None = None
    gradualAvailability: bool | None = None


class AppointmentConcurrencyLimit(BaseModel):
    weekDay: int
    afterTime: time
    maxConcurrent: int


class PatchAppointmentConcurrencyLimit(BaseModel):
    weekDay: int | None = None
    afterTime: time | None = None
    maxConcurrent: int | None = None


class ClosedDay(BaseModel):
    date: date
    note: str


class Address(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number: str
    street: str
    postcode: str
    city: str


class ExpenseType(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    description: str


class ContractType(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str

class AboutUs(BaseModel):
    html: str


class FaqBase(BaseModel):
    question: str
    answer: str

class Faq(FaqBase):
    id: UUID
    active: bool
    orderIndex: int

class UpdateFaq(FaqBase):
    active: bool
