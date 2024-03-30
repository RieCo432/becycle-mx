import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
import json
from os import path


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
