from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
import app.models as models
import app.dependencies as dep


public = APIRouter(
    tags=["public"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@public.get("/public/opening-hours")
def get_opening_times(db: Session = Depends(dep.get_db)) -> list[schemas.DayOpeningTimes]:

    return crud.get_opening_times(db=db)
