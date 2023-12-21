from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from sqlalchemy import select
from uuid import UUID


def get_contracts(client_id: UUID, db: Session) -> list[models.Contract]:
    return [contract for contract in db.scalars(
        select(models.Contract)
        .where(models.Contract.clientId == client_id)
    )]


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
