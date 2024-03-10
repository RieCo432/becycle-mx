from datetime import datetime, date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
import os


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


statistics = APIRouter(
    tags=["statistics"],
    responses={404: {"description": "Not Found"}}
)


@statistics.get("/statistics/users/leaderboard", dependencies=[Depends(dep.get_current_active_user)])
async def get_user_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.UserLeaderboard]:
    leaderboard = crud.get_user_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/clients/leaderboard", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.ClientLeaderboard]:
    leaderboard = crud.get_client_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/bikes/leaderboard", dependencies=[Depends(dep.get_current_active_user)])
async def get_bike_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.BikeLeaderboard]:
    leaderboard = crud.get_bike_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/contracts/total", dependencies=[Depends(dep.get_current_active_user)])
async def get_contracts_statistics(
        interval: int,
        breakdown: str,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_total_contracts_statistics(db=db, interval=interval, breakdown=breakdown)


@statistics.get("/statistics/contracts/active", dependencies=[Depends(dep.get_current_active_user)])
async def get_contracts_statistics(
        interval: int,
        grace_period: int,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_active_contracts_statistics(db=db, interval=interval, grace_period=grace_period)


@statistics.get("/statistics/contracts/new", dependencies=[Depends(dep.get_current_active_user)])
async def get_contracts_statistics(
        interval: int,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_new_contracts_statistics(db=db, interval=interval)
