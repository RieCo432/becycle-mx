import json
import random
import app.schemas as schemas
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

    if len(existing_segment) == 0:
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

    else:
        print("This Road Segment already exists")
        new_road_segment = None

    return new_road_segment


def get_bbox_geojson(db: Session, north_bound: float, east_bound: float, south_bound: float, west_bound: float, min_length: int = 0):
    road_segments = [_ for _ in db.scalars(
        select(models.RoadSegment)
        .where(
            (
                    (
                            (models.RoadSegment.fromLatitude < north_bound)
                            & (models.RoadSegment.fromLatitude > south_bound)
                            & (models.RoadSegment.fromLongitude < east_bound)
                            & (models.RoadSegment.fromLongitude > west_bound)
                    )
                    | (
                            (models.RoadSegment.toLatitude < north_bound)
                            & (models.RoadSegment.toLatitude > south_bound)
                            & (models.RoadSegment.toLongitude < east_bound)
                            & (models.RoadSegment.toLongitude > west_bound)
                    )
            )
            & (models.RoadSegment.length > min_length)
        )
    )]

    geojson_dict = {
        "type": "FeatureCollection",
        "name": "aberdeenroads",
        "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
        "bbox": [west_bound, south_bound, east_bound, north_bound],
        "features": []
    }

    for road_segment in road_segments:
        road_segment_reports = [_ for _ in db.scalars(
            select(models.RoadSegmentReport)
            .where(models.RoadSegmentReport.roadSegmentId == road_segment.id)
            .distinct(models.RoadSegmentReport.typeId)
        )]
        geojson_dict["features"].append(
            {"type": "Feature",
             "properties": {
                 "layer": "Roads",
                 "id": str(road_segment.id),
                 "reports": [{
                     'id': road_segment_report.type.id,
                     'title': road_segment_report.type.title,
                     'description': road_segment_report.type.description,
                     'scoreModifier': road_segment_report.type.scoreModifier
                 } for road_segment_report in road_segment_reports],
             },
             "geometry": {"type": "LineString", "coordinates": [
                 [road_segment.fromLongitude, road_segment.fromLatitude],
                 [road_segment.toLongitude, road_segment.toLatitude]
             ]}},
        )

    return json.dumps(geojson_dict)
