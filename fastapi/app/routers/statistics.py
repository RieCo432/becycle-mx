import os
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


statistics = APIRouter(
    tags=["statistics"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@statistics.get("/statistics/users/leaderboard")
async def get_user_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.UserLeaderboard]:
    leaderboard = crud.get_user_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/clients/leaderboard")
async def get_client_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.ClientLeaderboard]:
    leaderboard = crud.get_client_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/bikes/leaderboard")
async def get_bike_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.BikeLeaderboard]:
    leaderboard = crud.get_bike_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/contracts/total")
async def get_total_contracts_statistics(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_total_contracts_statistics(db=db, interval=interval, start_date=start, end_date=end)


@statistics.get("/statistics/contracts/active")
async def get_active_contracts_statistics(
        interval: str,
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_active_contracts_statistics(db=db, interval=interval, grace_period=grace_period, start_date=start, end_date=end)


@statistics.get("/statistics/contracts/new")
async def get_new_contracts_statistics(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_new_contracts_statistics(db=db, interval=interval, start_date=start, end_date=end)


@statistics.get("/statistics/contracts/returned")
async def get_returned_contracts_statistics(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_returned_contracts_statistics(db=db, interval=interval, start_date=start, end_date=end)


@statistics.get("/statistics/contracts/status")
async def get_contracts_percentage_returned_within_grace_period(
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> dict[str, int]:
    return crud.get_contracts_status(db=db, grace_period=grace_period, start_date=start, end_date=end)
