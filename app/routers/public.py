import datetime
from datetime import time
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

public = APIRouter(
    tags=["public"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@public.get("/public/opening-times")
def get_opening_times(db: Session = Depends(dep.get_db)) -> list[schemas.DayOpeningTimes]:
    return crud.get_opening_times(db=db)


@public.get("/public/opening-days")
def get_opening_days(db: Session = Depends(dep.get_db)) -> list[int]:
    return crud.get_opening_week_days(db=db)


@public.get("/public/opening-hours")
def get_opening_hours(db: Session = Depends(dep.get_db)) -> dict[str, time]:
    return crud.get_opening_hours(db=db)


@public.get("/public/slot-duration")
def get_slot_duration(db: Session = Depends(dep.get_db)) -> int:
    return crud.get_slot_duration(db=db)


@public.get("/public/next-closed-day")
def get_next_closed_day(db: Session = Depends(dep.get_db)) -> schemas.ClosedDay:
    return crud.get_closed_days(db=db, start_date=datetime.datetime.utcnow())[0]


@public.get("/public/address")
def get_address(db: Session = Depends(dep.get_db)) -> schemas.Address:
    return crud.get_address(db=db)


@public.get("/public/users/presentation-cards")
async def get_user_presentation_cards(
        db: Session = Depends(dep.get_db)
) -> list[schemas.UserPresentationCard]:
    return crud.get_user_presentation_cards(db=db)


@public.get("/public/users/presentation-cards/{card_id}/photo")
async def get_user_presentation_card_photo(
        card_id: UUID,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    return FileResponse(**crud.get_user_presentation_card_photo(db=db, card_id=card_id))
