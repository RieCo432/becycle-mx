from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from sqlalchemy import select


def get_bikes(make: str, model: str, colour: str, decals: str, serialNumber: str, db: Session) -> list[schemas.Bike]:
    return [bike for bike in db.scalars(
        select(models.Bike)
        .where(
            (models.Bike.make == make)
            | (models.Bike.model == model)
            | (models.Bike.colour == colour)
            | (models.Bike.decals == decals)
            | (models.Bike.serialNumber == serialNumber)
        )
    )]


def create_bike(bike_data: schemas.BikeCreate, db: Session) -> schemas.Bike:
    bike = models.Bike(
        make=bike_data.make,
        model=bike_data.model,
        colour=bike_data.colour,
        decals=bike_data.decals,
        serialNumber=bike_data.serialNumber
    )
    db.add(bike)
    db.commit()
    return bike
