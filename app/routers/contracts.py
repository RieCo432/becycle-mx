from fastapi import APIRouter, Depends
import app.schemas as schemas
import app.crud as crud
import app.dependencies as dep
from uuid import UUID
from sqlalchemy.orm import Session


contracts = APIRouter(
    tags=["contracts"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@contracts.get("/contracts")
async def get_contracts(
        client_id: UUID = None,
        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(client_id=client_id, db=db)


@contracts.post("/contract")
async def create_contract(
        contract_data: schemas.ContractCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Contract:
    return crud.create_contract(contract_data=contract_data, db=db)

