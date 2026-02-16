from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from starlette import status

from app import schemas, models, crud
from uuid import UUID

from app.services.accounts_helpers import AccountsHelpers
from typing import List


def get_account(db: Session, account_id: UUID) -> models.Account | None:
    return db.scalar(
        select(models.Account).where(models.Account.id == account_id)
    )


def create_account(new_account_data: schemas.AccountCreate, db: Session) -> models.Account:
    owner_user = None
    if new_account_data.ownerUserId is not None:
        owner_user = crud.users.get_user(db=db, user_id=new_account_data.ownerUserId)
        if owner_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner user not found")
    owner_group = None
    if new_account_data.ownerGroupId is not None:
        owner_group = crud.groups.get_group(db=db, group_id=new_account_data.ownerGroupId)
        if owner_group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner group not found")
        
    if new_account_data.type not in AccountsHelpers.types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account type")
    
    db_account = models.Account(
        name=new_account_data.name.lower(),
        description=new_account_data.description.lower(),
        showInUis=new_account_data.showInUis,
        ownerUserId=owner_user.id if owner_user is not None else None,
        ownerGroupId=owner_group.id if owner_group is not None else None,
        scheduledClosureDate=new_account_data.scheduledClosureDate,
        type=new_account_data.type.lower(),
        isInternal=new_account_data.isInternal
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, ui_filters: List[str] | None = None) -> list[models.Account]:
    filter_query = []
    if ui_filters is not None:
        filter_query.append(models.Account.showInUis.op('&&')(ui_filters))
    
    return [_ for _ in db.scalars(
        select(models.Account)
        .where(and_(*filter_query))
    )]

def update_account(db: Session, account_id: UUID, updated_account_data: schemas.AccountUpdate) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    if account is None:
        return None
    account.name = updated_account_data.name
    account.description = updated_account_data.description
    account.showInUis = updated_account_data.showInUis
    account.scheduledClosureDate = updated_account_data.scheduledClosureDate
    db.commit()
    db.refresh(account)
    return account

def close_account(account_id: UUID, db: Session, user: models.User) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    account.closedOn = datetime.now(timezone.utc)
    account.closedByUserId = user.id
    db.commit()
    db.refresh(account)
    return account

def reopen_account(account_id: UUID, db: Session) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    account.closedOn = None
    account.closedByUserId = None
    db.commit()
    db.refresh(account)
    return account