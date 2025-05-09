from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

bikes = APIRouter(
    tags=["bikes"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@bikes.get("/bike/find", dependencies=[Depends(dep.get_current_active_user)])
async def find_bike(
        make: str,
        model: str,
        colour: str,
        serial_number: str,
        decals: str = None,
        db: Session = Depends(dep.get_db)) -> schemas.Bike:
    return crud.find_similar_bikes(
        make=make.lower() if make is not None else None,
        model=model.lower() if model is not None else None,
        colour=colour.lower() if colour is not None else None,
        decals=decals.lower() if decals is not None else None,
        serialNumber=serial_number.lower() if serial_number is not None else None,
        db=db)[0]


@bikes.get("/bikes/find", dependencies=[Depends(dep.get_current_active_user)])
async def find_bikes(
        make: str | None = None,
        model: str | None = None,
        colour: str | None = None,
        serial_number: str | None = None,
        decals: str | None = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.Bike]:
    return crud.get_potential_bike_matches(
        make=make,
        model=model,
        colour=colour,
        decals=decals,
        serialNumber=serial_number,
        db=db)


@bikes.get("/bikes", dependencies=[Depends(dep.get_current_active_user)])
async def get_all_bikes(db: Session = Depends(dep.get_db)) -> list[schemas.Bike]:
    return crud.get_all_bikes(db=db)


@bikes.get("/bikes/{bike_id}")
async def get_bike(
        bike_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.get_bike(db=db, bike_id=bike_id)


@bikes.patch("/bikes/{bike_id}", dependencies=[Depends(dep.get_current_active_user)])
async def patch_bike(
        bike_id: UUID,
        updated_bike_data: schemas.BikeBase,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.update_bike(db=db, bike_id=bike_id, updated_bike_data=updated_bike_data)


@bikes.get("/bikes/tag/{rfid_tag_serial_number}", dependencies=[Depends(dep.get_current_active_user)])
async def get_bike_by_tag(
        rfid_tag_serial_number: str,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    bikes = crud.get_bikes_by_rfid_tag_serial_number(db=db, rfid_tag_serial_number=rfid_tag_serial_number)
    if len(bikes) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Bike not found"})

    return bikes[0]


@bikes.get("/bikes/{bike_id}/contracts", dependencies=[Depends(dep.get_current_active_user)])
async def get_bike_contracts(
        bike_id: UUID,
        db: Session = Depends(dep.get_db)
) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, bike_id=bike_id)


@bikes.post("/bike", dependencies=[Depends(dep.get_current_active_user)])
async def create_bike(
        bike_data: schemas.BikeCreate,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.create_bike(bike_data=bike_data, db=db)


@bikes.get("/bikes/suggest/makes", dependencies=[Depends(dep.get_current_active_user)])
async def get_make_suggestions(
        make: str,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_makes(db=db, make=make.lower())


@bikes.get("/bikes/suggest/models", dependencies=[Depends(dep.get_current_active_user)])
async def get_model_suggestions(
        model: str,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_models(db=db, model=model.lower())


@bikes.get("/bikes/suggest/serial-numbers", dependencies=[Depends(dep.get_current_active_user)])
async def get_serial_number_suggestions(
        serial_number: str,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_serial_numbers(db=db, serial_number=serial_number.lower())


@bikes.get("/bikes/suggest/colours", dependencies=[Depends(dep.get_current_active_user)])
async def get_colour_suggestions(
        colour: str,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_colours(db=db, colour=colour.lower())


@bikes.get("/bike/conditions", dependencies=[Depends(dep.get_current_active_user)])
async def get_bike_conditions() -> list[str]:
    return ["poor", "fair", "good", "excellent"]
