from datetime import date, datetime
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from sqlalchemy import select
from uuid import UUID
from fastapi import HTTPException, status
from dateutil.relativedelta import relativedelta


def get_contracts(db: Session, client_id: UUID = None, open: bool = True, closed: bool = True, expired: bool = True) -> list[models.Contract]:
    contracts = [_ for _ in db.scalars(
        select(models.Contract)
        .where(
            ((models.Contract.clientId == client_id) | (client_id == None))
            & (
                ((models.Contract.returnedDate != None) & closed)
                | ((models.Contract.returnedDate == None) & (models.Contract.endDate < datetime.utcnow().date()) & expired)
                | ((models.Contract.returnedDate == None) & (models.Contract.endDate > datetime.utcnow().date()) & open)
            )
        )
    )]

    return contracts


def get_contract_start_dates(db: Session) -> list[date]:
    return [_ for _ in db.scalars(
        select(models.Contract.startDate)
        .distinct()
    )]


def get_contract_returned_dates(db: Session) -> list[date]:
    return [_ for _ in db.scalars(
        select(models.Contract.returnedDate)
        .where(models.Contract.returnedDate != None)
        .distinct()
    )]


def get_contracts_by_start_date(db: Session, start_date: date) -> list[models.Contract]:
    return [_ for _ in db.scalars(
        select(models.Contract)
        .where(models.Contract.startDate == start_date)
    )]


def get_contracts_by_returned_date(db: Session, returned_date: date) -> list[models.Contract]:
    return [_ for _ in db.scalars(
        select(models.Contract)
        .where(models.Contract.returnedDate == returned_date)
    )]


def get_contracts_grouped_by_start_date(db: Session) -> dict[date, list[models.Contract]]:
    contracts_by_start_date = {start_date: get_contracts_by_start_date(db=db, start_date=start_date) for start_date in get_contract_start_dates(db=db)}
    return contracts_by_start_date


def get_contracts_grouped_by_returned_date(db: Session) -> dict[date, list[models.Contract]]:
    contracts_by_returned_date = {returned_date: get_contracts_by_returned_date(db=db, returned_date=returned_date) for returned_date in get_contract_returned_dates(db=db)}
    return contracts_by_returned_date


def get_contract(db: Session, contract_id: UUID) -> models.Contract:
    return db.scalar(
        select(models.Contract)
        .where(models.Contract.id == contract_id)
    )


def create_contract(
        contract_data: schemas.ContractCreate,
        working_user_id: UUID,
        checking_user_id: UUID,
        deposit_collecting_user_id: UUID,
        db: Session) -> models.Contract:

    contract = models.Contract(
        clientId=contract_data.clientId,
        bikeId=contract_data.bikeId,
        workingUserId=working_user_id,
        checkingUserId=checking_user_id,
        depositCollectingUserId=deposit_collecting_user_id,
        depositAmountCollected=contract_data.depositAmountCollected,
        conditionOfBike=contract_data.conditionOfBike,
        contractType=contract_data.contractType,
        notes=contract_data.notes
    )

    db.add(contract)
    db.commit()
    return contract


def return_contract(
        db: Session,
        contract_id: UUID,
        deposit_amount_returned: int,
        return_accepting_user_id: UUID,
        deposit_returning_user_id: UUID) -> models.Contract:

    contract = get_contract(db=db, contract_id=contract_id)

    if deposit_amount_returned > contract.depositAmountCollected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Amount returned is higher than amount collected!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    contract.returnAcceptingUserId = return_accepting_user_id
    contract.depositReturningUserId = deposit_returning_user_id
    contract.returnedDate = datetime.utcnow().date()
    contract.depositAmountReturned = deposit_amount_returned

    db.commit()

    return contract


def extend_contract(db: Session, contract_id: UUID) -> models.Contract:
    contract = get_contract(db=db, contract_id=contract_id)

    contract.endDate = (datetime.utcnow() + relativedelta(months=6)).date()

    db.commit()

    return contract
