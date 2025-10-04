from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from starlette import status

import app.models as models
import app.schemas as schemas


def get_bike(db: Session, bike_id: UUID) -> models.Bike:
    return db.scalar(
        select(models.Bike)
        .where(models.Bike.id == bike_id)
    )


def find_similar_bikes(db: Session, make: str | None = None, model: str | None = None, colour: str | None = None, decals: str | None = None, serialNumber: str | None = None) -> list[schemas.Bike]:
    bikes = [bike for bike in db.scalars(
        select(models.Bike)
        .where(
            (func.levenshtein(models.Bike.make, make) <= 2)
            & (func.levenshtein(models.Bike.model, model) <= 2)
            & (func.levenshtein(models.Bike.colour, colour) <= 2)
            & (func.levenshtein(models.Bike.serialNumber, serialNumber) <= 2)
        )
        .order_by(func.levenshtein(models.Bike.serialNumber, serialNumber))
    )]

    if len(bikes) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "No bikes found"})

    return bikes


def get_potential_bike_matches(db: Session, make: str | None = None, model: str | None = None, colour: str | None = None, colours: list[str] | None = None, decals: str | None = None, serialNumber: str | None = None, max_distance: int = 4) -> list[schemas.Bike]:
    query_filter = []
    if make is not None:
        query_filter.append(models.Bike.make.contains(make.lower()) | (func.levenshtein(models.Bike.make, make) <= max_distance))
    if model is not None:
        query_filter.append(models.Bike.model.contains(model.lower()) | (func.levenshtein(models.Bike.model, model) <= max_distance))
    if colour is not None:
        query_filter.append(models.Bike.colour.contains(colour.lower()) | (func.levenshtein(models.Bike.colour, colour) <= max_distance))
    if serialNumber is not None:
        query_filter.append(models.Bike.serialNumber.contains(serialNumber.lower()) | (func.levenshtein(models.Bike.serialNumber, serialNumber) <= max_distance))

    if colours is not None:
        colour_values = [models.Colour.getintvalue(colour) for colour in colours]
        query_filter.append(models.Bike.colours.any(models.Colour.id.in_(colour_values)))

    bikes = [bike for bike in db.scalars(
        select(models.Bike)
        .where(and_(*query_filter))
    )]

    return bikes


def get_all_bikes(db: Session) -> list[schemas.Bike]:
    return [_ for _ in db.scalars(
        select(models.Bike)
    )]

def get_bikes_by_rfid_tag_serial_number(db: Session, rfid_tag_serial_number: str) -> list[schemas.Bike]:
    bikes = [_ for _ in db.scalars(
        select(models.Bike)
        .where(models.Bike.rfidTagSerialNumber == rfid_tag_serial_number)
    )]
    return bikes


def create_bike(bike_data: schemas.BikeCreate, db: Session) -> schemas.Bike:
    bike = models.Bike(
        make=bike_data.make.lower(),
        model=bike_data.model.lower(),
        colour=bike_data.colour.lower(),
        decals=bike_data.decals.lower() if bike_data.decals is not None else None,
        serialNumber=bike_data.serialNumber.lower()
    )
    db.add(bike)
    db.commit()
    return bike


def get_similar_makes(db: Session, make: str, max_distance: int = 4) -> list[str]:
    similar_makes = [_ for _ in db.scalars(
        select(models.Bike.make)
        .where(models.Bike.make.contains(make) | (func.levenshtein(models.Bike.make, make) <= max_distance))
        .distinct()
    )]

    return similar_makes


def get_similar_models(db: Session, model: str, max_distance: int = 4) -> list[str]:
    similar_models = [_ for _ in db.scalars(
        select(models.Bike.model)
        .where(models.Bike.model.contains(model) | (func.levenshtein(models.Bike.model, model) <= max_distance))
        .distinct()
    )]

    return similar_models


def get_similar_serial_numbers(db: Session, serial_number: str, max_distance: int = 4) -> list[str]:
    similar_serial_numbers = [_ for _ in db.scalars(
        select(models.Bike.serialNumber)
        .where(models.Bike.serialNumber.contains(serial_number) | (func.levenshtein(models.Bike.serialNumber, serial_number) <= max_distance))
        .distinct()
    )]

    return similar_serial_numbers


def get_similar_colours(db: Session, colour: str, max_distance: int = 4) -> list[str]:
    similar_colours = [_ for _ in db.scalars(
        select(models.Bike.colour)
        .where(models.Bike.colour.contains(colour) | (func.levenshtein(models.Bike.colour, colour) <= max_distance))
        .distinct()
    )]

    return similar_colours


def get_similar_colour_sets(db: Session, colours: list[str], max_distance: int = 2) -> list[list[models.Colour]]:
    all_bikes = [_ for _ in db.scalars(
        select(models.Bike)
    )]
    # TODO: These need to be unique
    result = [bike.colours for bike in all_bikes if sum([0 if colour in colours else 1 for colour in [c.hex for c in bike.colours]]) <= max_distance]
    
    return result


def update_bike(db: Session, bike_id: UUID, updated_bike_data: schemas.BikeBase) -> models.Bike:
    bike = get_bike(db=db, bike_id=bike_id)
    if updated_bike_data.make is not None:
        bike.make = updated_bike_data.make.lower()
    if updated_bike_data.model is not None:
        bike.model = updated_bike_data.model.lower()
    if updated_bike_data.colour is not None:
        bike.colour = updated_bike_data.colour.lower()
    if updated_bike_data.colours is not None:
        colour_ids = [models.Colour.getintvalue(c.hex) for c in updated_bike_data.colours]
        colours = [_ for _ in db.scalars(
            select(models.Colour)
            .where(models.Colour.id.in_(colour_ids))
        )]
        bike.colours = colours
    if updated_bike_data.decals is not None:
        bike.decals = updated_bike_data.decals.lower()
    if updated_bike_data.serialNumber is not None:
        bike.serialNumber = updated_bike_data.serialNumber.lower()
    if updated_bike_data.rfidTagSerialNumber is not None:
        bike.rfidTagSerialNumber = updated_bike_data.rfidTagSerialNumber.lower()
        bikes_with_this_tag = get_bikes_by_rfid_tag_serial_number(db=db, rfid_tag_serial_number=updated_bike_data.rfidTagSerialNumber)
        for bike_with_this_tag in bikes_with_this_tag:
            if bike_with_this_tag.id != bike_id:
                bike_with_this_tag.rfidTagSerialNumber = "MOVED TO ANOTHER BIKE"


    db.commit()

    return bike
