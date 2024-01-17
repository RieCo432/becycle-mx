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


def get_similar_makes(db: Session, make: str) -> list[str]:
    similar_makes = [_ for _ in db.scalars(
        select(models.Bike.make)
        .where(models.Bike.make.startswith(make))
        .distinct()
    )]

    return similar_makes


def get_similar_models(db: Session, model: str) -> list[str]:
    similar_models = [_ for _ in db.scalars(
        select(models.Bike.model)
        .where(models.Bike.model.startswith(model))
        .distinct()
    )]

    return similar_models


def get_similar_serial_numbers(db: Session, serial_number: str) -> list[str]:
    similar_serial_numbers = [_ for _ in db.scalars(
        select(models.Bike.serialNumber)
        .where(models.Bike.serialNumber.startswith(serial_number))
        .distinct()
    )]

    return similar_serial_numbers
