from fastapi.security import OAuth2PasswordRequestForm
import app.models as models
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated
from app import auth
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import APIRouter, Depends


finances = APIRouter(
    tags=["finances"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@finances.get("/finances/deposit-book")
async def get_deposit_book(db: Session = Depends(dep.get_db)) -> schemas.DepositBalancesBook:
    return crud.get_deposit_balances_book(db=db)
