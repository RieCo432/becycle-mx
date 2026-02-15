from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select

from app import schemas, models
from uuid import UUID


def get_account(account_id: UUID, db: Session) -> models.Account | None:
    return db.scalar(
        select(models.Account).where(models.Account.id == account_id)
    )


def create_account(new_account_data: schemas.AccountCreate, db: Session) -> models.Account:
    db_account = models.Account(**new_account_data.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session) -> list[models.Account]:
    return [_ for _ in db.scalars(
        select(models.Account)
    )]

def update_account(db: Session, account_id: UUID, updated_account_data: schemas.AccountUpdate) -> models.Account:
    account = get_account(account_id=account_id, db=db)
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
    account = get_account(account_id=account_id, db=db)
    account.closedOn = datetime.now(timezone.utc)
    account.closedByUserId = user.id
    db.commit()
    db.refresh(account)
    return account