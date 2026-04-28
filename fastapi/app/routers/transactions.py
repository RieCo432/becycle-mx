from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session

import app.dependencies as dep
from app import models, schemas, crud

transactions = APIRouter(
    tags=["transactions"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.check_permissions)]
)

@transactions.get("/transactions", response_model=list[schemas.TransactionHeader])
async def get_transactions(db: Session = Depends(dep.get_db)):
    return crud.get_transaction_headers(db)

@transactions.get("/transactions/formatted", response_model=list[schemas.TransactionHeaderFormatted])
async def get_formatted_transactions(db: Session = Depends(dep.get_db)):
    return crud.get_formatted_transaction_headers(db)


@transactions.get("/transactions/events", response_model=List[str])
async def get_transaction_events(db: Session = Depends(dep.get_db)):
    return crud.get_transaction_events(db)


@transactions.post("/transactions", response_model=schemas.TransactionHeader)
async def create_transaction(
    transaction_data: schemas.TransactionCreate,
    user: models.User = Depends(dep.get_current_user),
    additional_active_users: list[models.User] | None = Depends(dep.get_active_users),
    db: Session = Depends(dep.get_db)
):
    transaction_header = crud.create_transaction(db, transaction_data, user, additional_active_users)

    return transaction_header

@transactions.patch("/transactions/{transaction_header_id}/post", response_model=schemas.TransactionHeader)
async def post_transaction_header(
        transaction_header_id: UUID,
        user: models.User = Depends(dep.get_current_user),
        additional_active_users: list[models.User] | None = Depends(dep.get_active_users),
        db: Session = Depends(dep.get_db)):
    
    return crud.post_transaction_header(db, transaction_header_id, user, additional_active_users)

