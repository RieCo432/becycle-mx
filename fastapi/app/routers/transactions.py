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


@transactions.post("/transactions", response_model=schemas.TransactionHeader)
def create_transaction(
    transaction_data: schemas.TransactionCreate,
    user: models.User = Depends(dep.get_current_user),
    db: Session = Depends(dep.get_db)
):
    return crud.create_transaction(db, transaction_data, user)

@transactions.patch("/transactions/{transaction_id}/post", response_model=schemas.TransactionHeader)
def post_transaction_header(transaction_header_id: UUID, user: models.User = Depends(dep.get_current_user), db: Session = Depends(dep.get_db)):
    return crud.post_transaction_header(db, transaction_header_id, user)

