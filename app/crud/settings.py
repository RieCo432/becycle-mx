import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import app.models as models
import app.schemas as schemas


def get_appointment_general_settings(db: Session) -> models.AppointmentGeneralSettings:
    appointment_general_settings = db.scalar(
        select(models.AppointmentGeneralSettings)
        .where(models.AppointmentGeneralSettings.id == 1)
    )

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
