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


@finances.get("/finances/deposit-book", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_book(db: Session = Depends(dep.get_db)) -> schemas.DepositBalancesBook:
    return crud.get_deposit_balances_book(db=db)


@finances.get("/finances/deposits/total", dependencies=[Depends(dep.get_current_active_user)])
async def get_total_deposits(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.DataSeries]:
    return crud.get_total_deposits(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/claimable", dependencies=[Depends(dep.get_current_active_user)])
async def get_claimable_deposits(
        interval: str,
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_claimable_deposits(db=db, interval=interval, grace_period=grace_period, start_date=start, end_date=end)


@finances.get("/finances/deposits/collected", dependencies=[Depends(dep.get_current_active_user)])
async def get_collected_deposits(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_collected_deposits(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/returned", dependencies=[Depends(dep.get_current_active_user)])
async def get_returned_deposits(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_returned_deposits(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/flow", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_flow(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_deposit_flow(db=db, interval=interval, start_date=start, end_date=end)


@finances.get("/finances/deposits/status", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposits_status(
        grace_period: int,
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> dict[str, int]:
    return crud.get_deposits_status(db=db, grace_period=grace_period, start_date=start, end_date=end)


@finances.get("/finances/deposits/return-percentage", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_return_percentage(
        start: date | None = None,
        end: date | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeriesWithType]:
    return crud.get_deposit_return_percentage(db=db, start_date=start, end_date=end)


@finances.get("/finances/deposits/required-float/worst-case", dependencies=[Depends(dep.get_current_active_user)])
async def get_worst_case_required_deposit_float(
        db: Session = Depends(dep.get_db)
) -> dict[str, int]:
    return crud.get_worst_case_required_deposit_float(db=db)


@finances.get("/finances/deposits/required-float/realistic", dependencies=[Depends(dep.get_current_active_user)])
async def get_realistic_case_required_deposit_float(
        grace_period: int,
        db: Session = Depends(dep.get_db)
) -> dict[str, int]:
    return crud.get_realistic_required_deposit_float(db=db, grace_period=grace_period)


@finances.get("/finances/cashflow/actual", dependencies=[Depends(dep.get_current_active_user)])
async def get_cashflow_actual(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        tag: str | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_actual_cashflow(db=db, interval=interval, start_date=start, end_date=end, tag_id=tag)


@finances.get("/finances/cashflow/provisional", dependencies=[Depends(dep.get_current_active_user)])
async def get_cashflow_provisional(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        tag: str | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_provisional_cashflow(db=db, interval=interval, start_date=start, end_date=end, tag_id=tag)


@finances.get("/finances/cashflow/total", dependencies=[Depends(dep.get_current_active_user)])
async def get_cashflow_total(
        interval: str,
        start: date | None = None,
        end: date | None = None,
        tag: str | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.DataSeries]:
    return crud.get_total_cashflow(db=db, interval=interval, start_date=start, end_date=end, tag_id=tag)
