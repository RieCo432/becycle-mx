from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

deposit_exchanges = APIRouter(
    tags=["deposit exchanges"],
    responses={404: {"description": "Not Found"}}
)


@deposit_exchanges.post("/deposit-exchanges", dependencies=[Depends(dep.get_current_active_user)])
async def create_deposit_exchange(
        amount: Annotated[int, Body()],
        from_user: models.User = Depends(dep.get_deposit_exchange_from_user),
        to_user: models.User = Depends(dep.get_deposit_exchange_to_user),
        db: Session = Depends(dep.get_db)) -> schemas.DepositExchange:

    if to_user.id == from_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "To and From cannot be the same!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    if (
            (to_user.username == 'BANK' and not from_user.treasurer)
            or (from_user.username == 'BANK' and not to_user.treasurer)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"description": "Only Treasurer can transfer deposits to the BANK"}
        )

    if amount > from_user.get_deposit_bearer_balance() and from_user.username != "BANK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "From User does not have enough funds!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    return crud.create_deposit_exchange(db=db, amount=amount, from_user_id=from_user.id, to_user_id=to_user.id)


@deposit_exchanges.get("/deposit-exchanges", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_exchanges(db: Session = Depends(dep.get_db)) -> list[schemas.DepositExchange]:
    return crud.get_deposit_exchanges(db=db)


@deposit_exchanges.get("/deposit-exchanges/users", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_exchange_users(db: Session = Depends(dep.get_db)) -> list[schemas.User]:
    return crud.get_deposit_exchange_users(db=db)
