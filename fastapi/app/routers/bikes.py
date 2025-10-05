from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

bikes = APIRouter(
    tags=["bikes"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@bikes.get("/bikes/first-match")
async def find_bike(
        make: str,
        model: str,
        serial_number: str,
        colours: str,
        db: Session = Depends(dep.get_db)) -> schemas.Bike:
    return crud.find_similar_bikes(
        make=make.lower() if make is not None else None,
        model=model.lower() if model is not None else None,
        colours=colours.split("|") if colours is not None else None,
        serialNumber=serial_number.lower() if serial_number is not None else None,
        db=db)[0]


@bikes.get("/bikes/find")
async def find_bikes(
        make: str | None = None,
        model: str | None = None,
        colour: str | None = None,
        colours: str | None = None,
        serial_number: str | None = None,
        decals: str | None = None,
        max_distance: int = 4,
        db: Session = Depends(dep.get_db)) -> list[schemas.Bike]:
    return crud.get_potential_bike_matches(
        make=make.lower() if make is not None else None,
        model=model.lower() if model is not None else None,
        colour=colour.lower() if colour is not None else None,
        colours=colours.split("|") if colours is not None else None,
        decals=decals.lower() if decals is not None else None,
        serialNumber=serial_number.lower() if serial_number is not None else None,
        max_distance=max_distance,
        db=db)


@bikes.get("/bikes")
async def get_all_bikes(db: Session = Depends(dep.get_db)) -> list[schemas.Bike]:
    return crud.get_all_bikes(db=db)


@bikes.get("/bikes/tag/{rfid_tag_serial_number}")
async def get_bike_by_tag(
        rfid_tag_serial_number: str,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    bikes = crud.get_bikes_by_rfid_tag_serial_number(db=db, rfid_tag_serial_number=rfid_tag_serial_number)
    if len(bikes) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Bike not found"})

    return bikes[0]


@bikes.post("/bikes")
async def create_bike(
        bike_data: schemas.BikeCreate,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.create_bike(bike_data=bike_data, db=db)


@bikes.get("/bikes/suggest/makes")
async def get_make_suggestions(
        make: str,
        max_distance: int = 4,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_makes(db=db, make=make.lower(), max_distance=max_distance)


@bikes.get("/bikes/suggest/models")
async def get_model_suggestions(
        model: str,
        max_distance: int = 4,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_models(db=db, model=model.lower(), max_distance=max_distance)


@bikes.get("/bikes/suggest/serial-numbers")
async def get_serial_number_suggestions(
        serial_number: str,
        max_distance: int = 4,
        db: Session = Depends(dep.get_db)
) -> list[str]:
    return crud.get_similar_serial_numbers(db=db, serial_number=serial_number.lower(), max_distance=max_distance)


@bikes.get("/bikes/suggest/colours")
async def get_colour_suggestions(
        colours: str,
        max_distance: int = 2,
        db: Session = Depends(dep.get_db)
) -> list[list[schemas.Colour]]:
    return crud.get_similar_colour_sets(db=db, colours=colours.split("|"), max_distance=max_distance)


@bikes.get("/bikes/conditions")
async def get_bike_conditions() -> list[str]:
    return ["poor", "fair", "good", "excellent"]


@bikes.get("/bikes/{bike_id}")
async def get_bike(
        bike_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.get_bike(db=db, bike_id=bike_id)


@bikes.patch("/bikes/{bike_id}")
async def patch_bike(
        bike_id: UUID,
        updated_bike_data: schemas.BikeBase,
        db: Session = Depends(dep.get_db)
) -> schemas.Bike:
    return crud.update_bike(db=db, bike_id=bike_id, updated_bike_data=updated_bike_data)


@bikes.get("/bikes/{bike_id}/contracts")
async def get_bike_contracts(
        bike_id: UUID,
        db: Session = Depends(dep.get_db)
) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, bike_id=bike_id)
