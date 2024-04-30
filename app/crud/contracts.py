from datetime import date, datetime
from uuid import UUID

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_contracts(db: Session, client_id: UUID | None = None, bike_id: UUID | None = None, open: bool = True, closed: bool = True, expired: bool = True) -> list[models.Contract]:
    primary_query_filter = []

    if client_id is not None:
        primary_query_filter.append((models.Contract.clientId == client_id))
    if bike_id is not None:
        primary_query_filter.append((models.Contract.bikeId == bike_id))

    contracts = [_ for _ in db.scalars(
        select(models.Contract)
        .where(
            and_(*primary_query_filter)
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


def get_client_contract(db: Session, client_id: UUID, contract_id: UUID) -> models.Contract:
    return db.scalar(
        select(models.Contract)
        .where(
            (models.Contract.id == contract_id)
            & (models.Contract.clientId == client_id)
        )
    )


def get_paper_contract_suggestions(db: Session, old_id: str) -> list[str]:
    return [_ for _ in db.scalars(
        select(models.PaperContract.id)
        .where(models.PaperContract.id.startswith(old_id))
    )]


def get_paper_contract(db: Session, paper_id: str) -> UUID:
    return db.scalar(
        select(models.PaperContract.contractId)
        .where(models.PaperContract.id == paper_id)
    )


def delete_contract(db: Session, contract_id: UUID) -> None:
    contract = get_contract(db=db, contract_id=contract_id)
    paper_contract = db.scalar(
        select(models.PaperContract)
        .where(models.PaperContract.contractId == contract_id)
    )
    if paper_contract is not None:
        db.delete(paper_contract)
        db.commit()
    db.delete(contract)
    db.commit()


def patch_contract_details(db: Session, contract_id: UUID, contract_patch_data: schemas.ContractPatch) -> models.Contract:
    contract = get_contract(db=db, contract_id=contract_id)

    if contract_patch_data.depositAmountCollected is not None:
        contract.depositAmountCollected = contract_patch_data.depositAmountCollected

    if contract_patch_data.conditionOfBike is not None:
        contract.conditionOfBike = contract_patch_data.conditionOfBike

    if contract_patch_data.contractType is not None:
        contract.contractType = contract_patch_data.contractType

    if contract_patch_data.notes is not None:
        contract.notes = contract_patch_data.notes

    if contract_patch_data.startDate is not None:
        contract.startDate = contract_patch_data.startDate

    if contract_patch_data.endDate is not None:
        contract.endDate = contract_patch_data.endDate

    if contract_patch_data.workingUserId is not None:
        contract.workingUserId = contract_patch_data.workingUserId

    if contract_patch_data.checkingUserId is not None:
        contract.checkingUserId = contract_patch_data.checkingUserId

    if contract_patch_data.depositCollectingUserId is not None:
        contract.depositCollectingUserId = contract_patch_data.depositCollectingUserId

    if contract_patch_data.returned:
        if contract_patch_data.depositAmountReturned is not None:
            contract.depositAmountReturned = contract_patch_data.depositAmountReturned

        if contract_patch_data.returnAcceptingUserId is not None:
            contract.returnAcceptingUserId = contract_patch_data.returnAcceptingUserId

        if contract_patch_data.depositReturningUserId is not None:
            contract.depositReturningUserId = contract_patch_data.depositReturningUserId

        if contract_patch_data.returnedDate is not None:
            contract.returnedDate = contract_patch_data.returnedDate
    else:
        contract.depositAmountReturned = None

        contract.returnAcceptingUserId = None

        contract.depositReturningUser = None

        contract.returnedDate = None

    db.commit()

    return contract


def get_contracts_for_expiry_email(db: Session) -> list[models.Contract]:
    ending_before = datetime.utcnow().date() + relativedelta(days=14)
    return [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(
                (models.Contract.returnedDate == None)
                & (models.Contract.expiryReminderSent == False)
                & (models.Contract.endDate < ending_before)
            )
        )
    ]


def send_expiry_emails(db: Session):
    for contract in get_contracts_for_expiry_email(db=db):
        contract.send_expiry_reminder_email()
        contract.expiryReminderSent = True
    db.commit()
