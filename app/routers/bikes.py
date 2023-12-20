from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
import app.models as models
import app.dependencies as dep


bikes = APIRouter(
    tags=["bikes"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@bikes.get("/bikes", dependencies=[Depends(dep.get_current_active_user)])
async def get_bikes(
        make: str = None,
        model: str = None,
        colour: str = None,
        decals: str = None,
        serial_number: str = None,
        db: Session = Depends(dep.get_db)
    ) -> list[schemas.Bike]:
    return crud.get_bikes(make=make, model=model, colour=colour, decals=decals, serialNumber=serial_number, db=db)


@bikes.post("/bike", dependencies=[Depends(dep.get_current_active_user)])
async def create_bike(
        bike_data: schemas.BikeCreate,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.create_bike(bike_data=bike_data, db=db)
