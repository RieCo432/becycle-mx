from fastapi import APIRouter, Depends
import app.schemas as schemas
import app.crud as crud
import app.dependencies as dep
from uuid import UUID
from sqlalchemy.orm import Session
import app.models as models


settings = APIRouter(
    tags=["settings"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@settings.get("/settings/appointments/general", dependencies=[Depends(dep.get_current_active_user)])
def get_appointment_general_settings(
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentGeneralSettings:

    return crud.get_appointment_general_settings(db=db)


@settings.get("/settings/appointments/concurrency", dependencies=[Depends(dep.get_current_active_user)])
def get_appointment_concurrency_limits(
        db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentConcurrencyLimit]:

    return crud.get_appointment_concurrency_limits(db=db)


@settings.post("/settings/appointments/concurrency", dependencies=[Depends(dep.get_current_appointment_manager_user)])
def create_appointment_concurrency_limit(
        appointment_concurrency_limit_data: schemas.AppointmentConcurrencyLimit,
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentConcurrencyLimit:

    return crud.add_appointment_concurrency_limit(
        db=db,
        appointment_concurrency_limit_data=appointment_concurrency_limit_data)

