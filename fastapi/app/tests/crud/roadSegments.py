import app.crud as crud
from app.tests.pytestFixtures import *


def test_create_road_segment_no_switch():
    road_segment = crud.create_road_segment(
        db=db,
        a_coords=(-2.196017, 57.160228),
        b_coords=(-2.195007, 57.169307),
        road_classification="Test Classification",
        road_function="driving",
        form_of_way="C Road",
        name="Test Street",
        length=1011
    )

    assert road_segment.fromLatitude == 57.160228
    assert road_segment.fromLongitude == -2.196017

    assert road_segment.toLatitude == 57.169307
    assert road_segment.toLongitude == -2.195007

    assert road_segment.roadClassification == "Test Classification"
    assert road_segment.roadFunction == "driving"
    assert road_segment.name == "Test Street"
    assert road_segment.formOfWay == "C Road"
    assert road_segment.length == 1011

    db.query(models.RoadSegment).delete()
    db.commit()


def test_create_road_segment_switch_a_and_b():
    road_segment = crud.create_road_segment(
        db=db,
        a_coords=(-2.195007, 57.169307),
        b_coords=(-2.196017, 57.160228),
        road_classification="Test Classification",
        road_function="driving",
        form_of_way="C Road",
        name="Test Street",
        length=1011
    )

    assert road_segment.fromLatitude == 57.160228
    assert road_segment.fromLongitude == -2.196017

    assert road_segment.toLatitude == 57.169307
    assert road_segment.toLongitude == -2.195007

    assert road_segment.roadClassification == "Test Classification"
    assert road_segment.roadFunction == "driving"
    assert road_segment.name == "Test Street"
    assert road_segment.formOfWay == "C Road"
    assert road_segment.length == 1011

    db.query(models.RoadSegment).delete()
    db.commit()


def test_create_road_segment_from_and_to_coordinate_sums_are_equal():
    with pytest.raises(Exception) as excinfo:
        crud.create_road_segment(
            db=db,
            a_coords=(-2.196017, 57.160228),
            b_coords=(-2.196027, 57.160238),
            road_classification="Test Classification",
            road_function="driving",
            form_of_way="C Road",
            name="Test Street",
            length=1011
        )

        assert excinfo.value == "Road Segment Error: A SUM == B SUM"


def test_create_road_segment_already_exists(road_segments):
    with pytest.raises(Exception) as excinfo:
        crud.create_road_segment(
            db=db,
            a_coords=(-2.196017, 57.160228),
            b_coords=(-2.195007, 57.169307),
            road_classification="Test Classification",
            road_function="driving",
            form_of_way="C Road",
            name="Test Street",
            length=1011
        )

        assert excinfo.value == "Road Segment"


