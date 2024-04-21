from os import path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app.services import distance

maps = APIRouter(
    tags=["maps"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@maps.get("/maps/geojson")
async def get_maps_geojson():
    with open(path.join(path.dirname(path.dirname(path.abspath(__file__))), "data", "aberdeenroads.geojson"), "r") as fin:
        geojson = fin.read()

    return geojson


@maps.get("/maps/bbox-road-map")
async def get_bbox_geojson(north_bound: float, east_bound: float, south_bound: float, west_bound: float, db: Session = Depends(dep.get_db)):
    diagonal_distance = distance(south_bound, west_bound, north_bound, east_bound)
    min_length = diagonal_distance // 1200
    return crud.get_bbox_geojson(db=db, north_bound=north_bound, east_bound=east_bound, south_bound=south_bound, west_bound=west_bound, min_length=min_length)


@maps.get("/maps/report-types")
async def get_report_types(db: Session = Depends(dep.get_db)) -> list[schemas.RoadSegmentReportType]:
    return crud.get_road_segment_report_types(db=db)


@maps.post("/maps/road-segment/report")
async def get_road_reports(report_data: schemas.NewRoadSegmentReport, db: Session = Depends(dep.get_db)):
    return crud.create_road_segment_report(db=db, road_segment_id=report_data.roadSegmentId, road_segment_report_type_id=report_data.roadSegmentReportTypeId)