from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from fastapi.params import Query
from sqlalchemy.orm import Session

import app.dependencies as dep
from app import models, schemas, crud
from typing import List, Annotated

accounts = APIRouter(
    tags=["accounts"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.check_permissions)]
)


@accounts.get("/accounts")
async def get_accounts(
        ui_filters: Annotated[List[str] | None, Query()] = None, 
        types: Annotated[List[str] | None, Query()] = None,
        projectId: str | None = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.Account]:
    return crud.get_accounts(db=db, ui_filters=ui_filters, types=types, projectId=projectId)


@accounts.get("/accounts/{account_id}")
async def get_account(account_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Account:
    account = crud.get_account(db=db, account_id=account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": f"Account with ID {account_id} not found"}
        )
    return account

@accounts.post("/accounts")
async def create_account(new_account_data: schemas.AccountCreate, db: Session = Depends(dep.get_db)) -> schemas.Account:
    return crud.create_account(db=db, new_account_data=new_account_data)

@accounts.put("/accounts/{account_id}")
async def update_account(account_id: UUID, updated_account_data: schemas.AccountUpdate, db: Session = Depends(dep.get_db)) -> schemas.Account:
    return crud.update_account(db=db, account_id=account_id, updated_account_data=updated_account_data)

@accounts.patch("/accounts/{account_id}/close")
async def close_account(account_id: UUID, db: Session = Depends(dep.get_db), user: models.User = Depends(dep.get_current_active_user)) -> schemas.Account:
    account = crud.get_account(db=db, account_id=account_id)
    if account.balance != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Account balance must be zero to close it."}
        )
    if account.closedOn is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Account is already closed."}
        )
    return crud.close_account(db=db, account_id=account_id, user=user)

@accounts.patch("/accounts/{account_id}/reopen")
async def reopen_account(account_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Account:
    account = crud.get_account(db=db, account_id=account_id)
    if account.closedOn is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Account is not closed."}
        )
    return crud.reopen_account(db=db, account_id=account_id)