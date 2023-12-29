from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
import app.models as models


deposit_exchanges = APIRouter(
    tags=["deposit exchanges"],
    responses={404: {"description": "Not Found"}}
)


@deposit_exchanges.post("/deposit-exchange", dependencies=[Depends(dep.get_current_active_user)])
async def create_deposit_exchange(
        deposit_exchange_data: schemas.DepositExchangeCreate,
        from_user: models.User = Depends(dep.get_deposit_giving_user),
        to_user: models.User = Depends(dep.get_deposit_receiving_user),
        db: Session = Depends(dep.get_db)) -> schemas.DepositExchange:

    if to_user.id == from_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "To and From cannot be the same!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    # TODO: check that giving volunteer has enough funds

    return crud.create_deposit_exchange(db=db, deposit_exchange_data=deposit_exchange_data, from_user_id=from_user.id, to_user_id=to_user.id)


@deposit_exchanges.get("/deposit-exchanges", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_exchanges(db: Session = Depends(dep.get_db)) -> list[schemas.DepositExchange]:
    return crud.get_deposit_exchanges(db=db)

