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


@finances.get("/finances/deposits/collected")
async def get_deposits_collected(
        interval: int,
        start_date: date | None = None,
        end_date: date | None = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.DateSeries]:
    return crud.get_deposits_collected(db=db, interval=interval, start_date=start_date, end_date=end_date)
