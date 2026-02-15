from uuid import UUID

from fastapi import HTTPException
from starlette import status

from app import models, crud, schemas
from sqlalchemy.orm import Session, SessionTransaction
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone


def get_transaction_headers(db: Session) -> list[models.TransactionHeader]:
    return [_ for _ in db.scalars(
        select(models.TransactionHeader)
    )]

def create_transaction_header(db: Session, transaction_header_data: schemas.TransactionHeaderCreate) -> models.TransactionHeader:
    pass

def create_transaction_lines(db: Session, transaction_lines_data: List[schemas.TransactionLineCreate]) -> models.TransactionHeader:
    pass
    
    
def create_transaction(db: Session, transaction_data: schemas.TransactionCreate, user: models.User) -> models.TransactionHeader:
    transaction_header = models.TransactionHeader(
        event=transaction_data.transactionHeader.event,
        createdOn=datetime.now(timezone.utc),
        createdByUserId=user.id
    )
    db.add(transaction_header)
    db.flush()
    db.refresh(transaction_header)
    
    for transaction_line_data in transaction_data.transactionLines:
        
        account = crud.accounts.get_account(db, transaction_line_data.accountId)
        if account is None:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Account not found"})
        if account.closedOn is not None:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": f"Account {account.name} is closed"})
        
        transaction_line = models.TransactionLine(
            transactionHeaderId=transaction_header.id,
            accountId=transaction_line_data.accountId,
            amount=transaction_line_data.amount
        )
        db.add(transaction_line)
    
    db.flush()
    
    for transaction_line in transaction_header.transactionLines:
        if transaction_line.account.normalisedBalance < 0 and not transaction_line.account.isAllowedNegative:
            account_name = transaction_line.account.name
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description":
                f"Account {account_name} has insufficient funds!"})
    
    if not transaction_header.doesBalance:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Transaction does not balance!"})
    
    db.commit()
    return transaction_header


def get_transaction_line(db, transaction_line_id):
    transaction_line = db.scalar(
        select(models.TransactionLine)
        .where(models.TransactionLine.id == transaction_line_id)
    )
    if transaction_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Transaction line not found"})
    return transaction_line


def can_transaction_line_be_posted(db: Session, transaction_line_id: UUID, user: models.User) -> bool:
    transaction_line = get_transaction_line(db, transaction_line_id)
    if transaction_line.account.closedOn is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": f"Account {transaction_line.account.name} is closed"})
    if (
            # if the account is not owned by any user or not by this user
            (
                    transaction_line.account.ownerUserId is None 
                    or transaction_line.account.ownerUserId != user.id
            ) 
            # and the account is not owned by any group or not by one of this user's groups
            and
            (
                    transaction_line.account.ownerGroupId is None 
                    or transaction_line.account.ownerGroupId not in [group.id for group in user.groups]
            )
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"description": "You are not allowed to post transactions on one of these accounts"})
    

    return True
        
    
def post_transaction_header(db: Session, transaction_header_id: UUID, user: models.User) -> models.TransactionHeader:
    transaction_header = db.scalar(
            select(models.TransactionHeader)
            .where(models.TransactionHeader.id == transaction_header_id)
    )
    
    if transaction_header.postedOn is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This transaction has already been posted!"})
            
            
    can_all_lines_be_posted = True
    for transaction_line in transaction_header.transactionLines:
        can_all_lines_be_posted &= can_transaction_line_be_posted(db, transaction_line.id, user)
        
    if can_all_lines_be_posted:
        transaction_header.postedOn = datetime.now(timezone.utc)
        transaction_header.postedByUserId = user.id
    
        db.commit()
        db.refresh(transaction_header)
        
    return transaction_header
    

    

