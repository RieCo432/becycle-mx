from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AppointmentBase(BaseModel):
    typeId: str
    startDateTime: datetime
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    clientId: UUID
    

class AppointmentReschedule(AppointmentBase):
    pass


class AppointmentRequest(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    id: UUID
    clientId: UUID
    endDateTime: datetime
    confirmed: bool = False
    cancelled: bool = False
    reminderSent: bool = False
    cancellationReason: str | None = None


class AppointmentCancellationDetail(BaseModel):
    reason: str | None = None