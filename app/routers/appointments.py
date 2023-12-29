from fastapi import APIRouter, Depends
import app.models as models
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated

appointments = APIRouter(
    tags=["appointments"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@appointments.post("/appointment")
async def request_appointment(
        appointment_data: schemas.AppointmentRequest,
        client: Annotated[models.Client, Depends(dep.get_current_client)],
        db: Session = Depends(dep.get_db)) -> schemas.Appointment:

    return crud.request_appointment(db=db, appointment_data=appointment_data, client_id=client.id)