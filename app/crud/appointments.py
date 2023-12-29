from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .settings import *
from uuid import UUID


def create_appointment(db: Session, appointment_data: schemas.AppointmentCreate) -> models.Appointment:
    # this is to be used by volunteers at the workshop. Client ID is specified in advance and the appointment is confirmed immediately
    appointment_type = get_appointment_type(db=db, appointment_type_id=appointment_data.typeId)

    appointment = models.Appointment(
        clientId=appointment_data.clientId,
        typeId=appointment_data.typeId,
        startDateTime=appointment_data.startDateTime,
        endDateTime=appointment_data.startDateTime + relativedelta(minutes=appointment_type.duration),
        notes=appointment_data.notes,
        confirmed=True
    )

    db.add(appointment)
    db.commit()

    # TODO: send confirmation email

    return appointment


def request_appointment(db: Session, appointment_data: schemas.AppointmentRequest, client_id: UUID) -> models.Appointment:
    # This is what clients use to request an appointment. The Client ID is pulled from the logged in client and the appointment must be confirmed separately
    appointment_type = get_appointment_type(db=db, appointment_type_id=appointment_data.typeId)

    appointment = models.Appointment(
        clientId=client_id,
        typeId=appointment_data.typeId,
        startDateTime=appointment_data.startDateTime,
        endDateTime=appointment_data.startDateTime + relativedelta(minutes=appointment_type.duration),
        notes=appointment_data.notes
    )

    db.add(appointment)
    db.commit()

    # TODO: send confirmation of reception of request

    return appointment
