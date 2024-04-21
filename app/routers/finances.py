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
