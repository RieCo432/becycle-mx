from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
import json


test_client = TestClient(app)


def test_bbox_geojson_view_1(road_segments, road_segment_reports):
    response = test_client.get("/maps/bbox-road-map", params={
        "north_bound": 57.175760756497226,
        "east_bound":-2.1331501007080083,
        "south_bound":57.140850001222105,
        "west_bound": -2.271080017089844
    })

    expected_segments = road_segments[0:3] + road_segments[10: ]

    assert response.status_code == 200
    response_json = json.loads(response.json())

    assert response_json["type"] == "FeatureCollection"
    assert response_json["name"] == "aberdeenroads"
    assert response_json["crs"] == {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}

    assert all([
        {"type": "Feature",
         "properties": {
             "layer": "Roads",
             "id": str(road_segment.id),
             "reports": [{
                     'id': road_segment_report.type.id,
                     'title': road_segment_report.type.title,
                     'description': road_segment_report.type.description,
                     'scoreModifier': road_segment_report.type.scoreModifier
                 } for road_segment_report in [rsr for rsr in road_segment_reports if rsr.roadSegmentId == road_segment.id]],
         },
         "geometry": {"type": "LineString", "coordinates": [
             [road_segment.fromLongitude, road_segment.fromLatitude],
             [road_segment.toLongitude, road_segment.toLatitude]
         ]}}
        in response_json["features"] for road_segment in expected_segments
    ])


def test_bbox_geojson_view_2(road_segments, road_segment_reports):
    response = test_client.get("/maps/bbox-road-map", params={
        "north_bound": 57.213566803525396,
        "east_bound": -2.0668029785156254,
        "south_bound": 57.17869175976932,
        "west_bound": -2.2047328948974614
    })

    expected_segments = road_segments[3:10]

    assert response.status_code == 200
    response_json = json.loads(response.json())

    assert response_json["type"] == "FeatureCollection"
    assert response_json["name"] == "aberdeenroads"
    assert response_json["crs"] == {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}

    assert all([
        {"type": "Feature",
         "properties": {
             "layer": "Roads",
             "id": str(road_segment.id),
             "reports": [{
                     'id': road_segment_report.type.id,
                     'title': road_segment_report.type.title,
                     'description': road_segment_report.type.description,
                     'scoreModifier': road_segment_report.type.scoreModifier
                 } for road_segment_report in [rsr for rsr in road_segment_reports if rsr.roadSegmentId == road_segment.id]],
         },
         "geometry": {"type": "LineString", "coordinates": [
             [road_segment.fromLongitude, road_segment.fromLatitude],
             [road_segment.toLongitude, road_segment.toLatitude]
         ]}}
        in response_json["features"] for road_segment in expected_segments
    ])


def test_get_report_types(road_segment_report_types):
    response = test_client.get("/maps/report-types")

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(road_segment_report_types)
    assert all([rsr in road_segment_report_types for rsr in response_json])


def test_post_road_segment_report_first_report(road_segment_report_types, road_segments, road_segment_reports):
    assert db.scalar(
        select(models.RoadSegmentReport)
        .where(models.RoadSegmentReport.roadSegmentId == road_segments[0].id)
    ) is None

    response = test_client.post("/maps/road-segment/report", json={
        "roadSegmentId": str(road_segments[0].id),
        "roadSegmentReportTypeId": str(road_segment_report_types[0].id)
    })

    assert response.status_code == 200
    response_json = json.loads(response.json())

    first_report = db.scalar(
        select(models.RoadSegmentReport)
        .where(models.RoadSegmentReport.roadSegmentId == road_segments[0].id)
    )

    assert first_report is not None

    assert response_json == {"type": "Feature",
         "properties": {
             "layer": "Roads",
             "id": str(road_segments[0].id),
             "reports": [{
                     'id': road_segment_report.type.id,
                     'title': road_segment_report.type.title,
                     'description': road_segment_report.type.description,
                     'scoreModifier': road_segment_report.type.scoreModifier
                 } for road_segment_report in [first_report]],
         },
         "geometry": {"type": "LineString", "coordinates": [
             [road_segments[0].fromLongitude, road_segments[0].fromLatitude],
             [road_segments[0].toLongitude, road_segments[0].toLatitude]
         ]}}

def test_post_road_segment_report_second_report(road_segment_report_types, road_segments, road_segment_reports):
    assert db.scalar(
        select(models.RoadSegmentReport)
        .where(models.RoadSegmentReport.roadSegmentId == road_segments[4].id)
    ) is not None

    response = test_client.post("/maps/road-segment/report", json={
        "roadSegmentId": str(road_segments[4].id),
        "roadSegmentReportTypeId": str(road_segment_report_types[0].id)
    })

    assert response.status_code == 200
    response_json = json.loads(response.json())

    second_report = db.scalar(
        select(models.RoadSegmentReport)
        .where(
            (models.RoadSegmentReport.roadSegmentId == road_segments[4].id)
            & (models.RoadSegmentReport.typeId == road_segment_report_types[0].id)
        )
    )

    assert second_report is not None

    assert response_json == {"type": "Feature",
                             "properties": {
                                 "layer": "Roads",
                                 "id": str(road_segments[4].id),
                                 "reports": [{
                                     'id': road_segment_report.type.id,
                                     'title': road_segment_report.type.title,
                                     'description': road_segment_report.type.description,
                                     'scoreModifier': road_segment_report.type.scoreModifier
                                 } for road_segment_report in [rsr for rsr in road_segment_reports + [second_report] if
                                                               rsr.roadSegmentId == road_segments[4].id]]
                             },
                             "geometry": {"type": "LineString", "coordinates": [
                                 [road_segments[4].fromLongitude, road_segments[4].fromLatitude],
                                 [road_segments[4].toLongitude, road_segments[4].toLatitude]
                             ]}}


def test_post_road_segment_report_same_report_type(road_segment_report_types, road_segments, road_segment_reports):
    assert db.scalar(
        select(models.RoadSegmentReport)
        .where(models.RoadSegmentReport.roadSegmentId == road_segments[4].id)
    ) is not None

    response = test_client.post("/maps/road-segment/report", json={
        "roadSegmentId": str(road_segments[4].id),
        "roadSegmentReportTypeId": str(road_segment_report_types[1].id)
    })

    assert response.status_code == 200
    response_json = json.loads(response.json())

    all_reports_of_this_type_for_this_segment = [_ for _ in db.scalars(
        select(models.RoadSegmentReport)
        .where(
            (models.RoadSegmentReport.roadSegmentId == road_segments[4].id)
            & (models.RoadSegmentReport.typeId == road_segment_report_types[1].id)
        )
    )]

    assert len(all_reports_of_this_type_for_this_segment) == 2

    assert response_json == {"type": "Feature",
                             "properties": {
                                 "layer": "Roads",
                                 "id": str(road_segments[4].id),
                                 "reports": [{
                                     'id': road_segment_report.type.id,
                                     'title': road_segment_report.type.title,
                                     'description': road_segment_report.type.description,
                                     'scoreModifier': road_segment_report.type.scoreModifier
                                 } for road_segment_report in [rsr for rsr in road_segment_reports if
                                                               rsr.roadSegmentId == road_segments[4].id]]
                             },
                             "geometry": {"type": "LineString", "coordinates": [
                                 [road_segments[4].fromLongitude, road_segments[4].fromLatitude],
                                 [road_segments[4].toLongitude, road_segments[4].toLatitude]
                             ]}}

    assert len(response_json.get("properties").get("reports")) == 1
