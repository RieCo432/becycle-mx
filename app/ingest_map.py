import json

import app.crud as crud
import app.models as models
from app.database.db import SessionLocal
from app.services import distance

db = SessionLocal()

db.query(models.RoadSegmentReport).delete()
db.query(models.RoadSegment).delete()

with open("data/aberdeenroads.geojson", "r") as fin:
    geojson_content = json.load(fin)

aberdeen_roads = geojson_content["features"]

for road in aberdeen_roads:
    road_function = road["properties"]["roadFunction"]
    road_classification = road["properties"]["roadClassification"]
    form_of_way = road["properties"]["formOfWay"]
    name = road["properties"]["name1"]
    length = road["properties"]["length"]
    road_coords = road["geometry"]["coordinates"]

    geometry_type = road["geometry"]["type"]

    if geometry_type != "LineString":
        raise Exception("Not LineString")

    a_coords_index = 0
    b_coords_index = 1

    sum_of_segments_length = 0

    while b_coords_index < len(road_coords):
        a_coords = road_coords[a_coords_index]
        b_coords = road_coords[b_coords_index]

        # length of the segment in meters

        segment_length = distance(a_coords[1], a_coords[0], b_coords[1], b_coords[0])

        sum_of_segments_length += segment_length

        crud.create_road_segment(db=db, a_coords=a_coords, b_coords=b_coords, road_classification=road_classification,
                                 road_function=road_function, form_of_way=form_of_way, name=name, length=round(segment_length))

        a_coords_index += 1
        b_coords_index += 1

    # if sum of segment length is more than two times the stated length of road and is longer than 500m, raise Exception
    if (length is not None
            and length * 1.1 < sum_of_segments_length < length * 0.9):
        print("Sum of lengths of segments does too different from the stated length for the road", length, sum_of_segments_length)


print("THIS IS THE END; MY ONLY FRIEND, THE END")