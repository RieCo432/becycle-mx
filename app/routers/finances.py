from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

finances = APIRouter(
    tags=["finances"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@finances.get("/finances/deposit-book")
async def get_deposit_book(db: Session = Depends(dep.get_db)) -> schemas.DepositBalancesBook:
    return crud.get_deposit_balances_book(db=db)


@finances.get("/finances/deposits/total")
async def get_total_deposits(
        interval: int,
        start_date: date | None = None,
        end_date: date | None = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.DateSeries]:
    return crud.get_total_deposits(db=db, interval=interval, start_date=start_date, end_date=end_date)


@finances.get("/finances/deposits/claimable", dependencies=[Depends(dep.get_current_active_user)])
async def get_claimable_deposits(
        interval: int,
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_claimable_deposits(db=db, interval=interval, grace_period=grace_period, start_date=start, end_date=end)


@finances.get("/finances/deposits/collected", dependencies=[Depends(dep.get_current_active_user)])
async def get_collected_deposits(
        interval: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_collected_deposits(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/returned", dependencies=[Depends(dep.get_current_active_user)])
async def get_returned_deposits(
        interval: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_returned_deposits(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/flow", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_flow(
        interval: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DateSeries]:
    return crud.get_deposit_flow(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/status", dependencies=[Depends(dep.get_current_active_user)])
async def get_contracts_percentage_returned_within_grace_period(
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> dict[str, int]:
    return crud.get_deposits_status(db=db, grace_period=grace_period, start_date=start, end_date=end)
