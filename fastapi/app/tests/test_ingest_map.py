from sqlalchemy import select
from app.tests.pytestFixtures import *
from app.ingest_map import ingest_map


def test_ingest_map():
    from_latitudes = [57.160228, 57.152243, 57.141279, 57.192152, 57.192543, 57.192543, 57.186599, 57.185582, 57.194733,
                      57.19442, 57.174394, 57.173533, 57.168055, 57.166177]
    from_longitudes = [-2.196017, -2.197316, -2.199048, -2.166281, -2.145495, -2.120667, -2.122976, -2.123265,
                       -2.139143,
                       -2.137267, -2.234991, -2.236723, -2.205544, -2.203667]
    to_latitudes = [57.169307, 57.160228, 57.152243, 57.192543, 57.192543, 57.192309, 57.188085, 57.186599, 57.19442,
                    57.194264, 57.175255, 57.174394, 57.167116, 57.167116]
    to_longitudes = [-2.195007, -2.196017, -2.197316, -2.145495, -2.120667, -2.086456, -2.122976, -2.122976, -2.137267,
                     -2.135823, -2.233548, -2.234991, -2.204534, -2.204534]
    road_classifications = ["A Road", "A Road", "A Road", "A Road", "A Road", "A Road", "B Road", "B Road", "B Road",
                            "B Road", "B Road", "B Road", "B Road", "B Road"]
    road_functions = ["A Road", "A Road", "A Road", "A Road", "A Road", "A Road", "B Road", "B Road", "B Road",
                      "B Road",
                      "B Road", "B Road", "B Road", "B Road"]
    form_of_ways = ["Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Dual Carriageway",
                    "Dual Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway",
                    "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway",
                    "Single Carriageway"]
    names = ["Big Street One", "Big Street One", "Big Street One", "Big Street Two", "Big Street Two", "Big Street Two",
             "Small Street One", "Small Street One", "Small Street Two", "Small Street Two", "Small Street Three",
             "Small Street Three", "Small Street Four", "Small Street Four"]
    lengths = [1011, 891, 1224, 1253, 1496, 2061, 165, 114, 118, 89, 129, 142, 121, 117]

    tests_directory = os.path.dirname(__file__)
    photos_directory = os.path.join(tests_directory, "photos")
    geojson_filepath = os.path.join(photos_directory, "aberdeenroads_tests.geojson")
    ingest_map(geojson_filepath)

    for i in range(14):
        assert db.scalar(
            select(models.RoadSegment)
            .where(
                (models.RoadSegment.fromLatitude == from_latitudes[i])
                & (models.RoadSegment.fromLongitude == from_longitudes[i])
                & (models.RoadSegment.toLatitude == to_latitudes[i])
                & (models.RoadSegment.toLongitude == to_longitudes[i])
                & (models.RoadSegment.roadClassification == road_classifications[i])
                & (models.RoadSegment.roadFunction == road_functions[i])
                & (models.RoadSegment.formOfWay == form_of_ways[i])
                & (models.RoadSegment.name == names[i])
                & (models.RoadSegment.length == lengths[i])
            )
        ) is not None