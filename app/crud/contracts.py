import datetime
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from sqlalchemy import select
from uuid import UUID
from fastapi import HTTPException, status


def get_contracts(db: Session) -> list[models.Contract]:
    return [contract for contract in db.scalars(
        select(models.Contract)
    )]


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
        contract_return_details: schemas.ContractReturn,
        return_accepting_user_id: UUID,
        deposit_returning_user_id: UUID) -> models.Contract:

    contract = get_contract(db=db, contract_id=contract_return_details.id)

    if contract_return_details.depositAmountReturned > contract.depositAmountCollected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Amount returned is higher than amount collected!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    contract.returnAcceptingUserId = return_accepting_user_id
    contract.depositReturningUserId = deposit_returning_user_id
    contract.returnedDate = datetime.datetime.utcnow()
    contract.depositAmountReturned = contract_return_details.depositAmountReturned

    db.commit()

    return contract
