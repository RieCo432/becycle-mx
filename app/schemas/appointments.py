from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class AppointmentBase(BaseModel):
    clientId: UUID
    appointmentTypeId: str
    startDateTime: datetime
    endDateTime: datetime
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    id: UUID
    confirmed: bool = False
    cancelled: bool = False
    reminderSent: bool = False