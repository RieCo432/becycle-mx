import app.models as models
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def create_road_segment(db: Session,
                        a_coords: tuple[float, float],
                        b_coords: tuple[float, float],
                        road_classification: str | None = None,
                        road_function: str | None = None,
                        form_of_way: str | None = None,
                        name: str | None = None,
                        length: int | None = None) -> models.RoadSegment:

    from_coords = None
    to_coords = None

    # SUM the coordinates of each point and select the smaller sum as FROM and the larger sum as TO
    a_coords_sum = sum(a_coords)
    b_coords_sum = sum(b_coords)

    if a_coords_sum < b_coords_sum:
        from_coords = a_coords
        to_coords = b_coords
    elif b_coords_sum < a_coords_sum:
        from_coords = b_coords
        to_coords = a_coords
    elif a_coords_sum == b_coords_sum:
        raise Exception("Road Segment Error: A SUM == B SUM")

    from_latitude = from_coords[1]
    from_longitude = from_coords[0]

    to_latitude = to_coords[1]
    to_longitude = to_coords[0]


    existing_segment = [_ for _ in db.scalars(
        select(models.RoadSegment)
        .where(
            (models.RoadSegment.fromLatitude == from_latitude)
            & (models.RoadSegment.fromLongitude == from_longitude)
            & (models.RoadSegment.toLatitude == to_latitude)
            & (models.RoadSegment.toLongitude == to_longitude)
        )
    )]

    if len(existing_segment) > 0:
        raise IntegrityError("This Road Segment already exists")

    new_road_segment = models.RoadSegment(
        fromLatitude=from_latitude,
        fromLongitude=from_longitude,
        toLatitude=to_latitude,
        toLongitude=to_longitude,
        roadClassification=road_classification,
        roadFunction=road_function,
        formOfWay=form_of_way,
        name=name,
        length=length
    )

    db.add(new_road_segment)
    db.commit()

    return new_road_segment