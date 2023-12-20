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


def create_contract(contract_data: schemas.ContractCreate, db: Session) -> models.Contract:
    contract = models.Contract(
        clientId=contract_data.clientId,
        bikeId=contract_data.bikeId,
        workingUserId=contract_data.workingUserId,
        checkingUserId=contract_data.checkingUserId,
        depositCollectingUserId=contract_data.depositCollectingUserId,
        depositAmountCollected=contract_data.depositAmountCollected,
        conditionOfBike=contract_data.conditionOfBike,
        contractType=contract_data.contractType,
        notes=contract_data.notes
    )

    db.add(contract)
    db.commit()
    return contract
