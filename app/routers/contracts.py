from fastapi import APIRouter, Depends, HTTPException, status
import app.schemas as schemas
import app.crud as crud
import app.dependencies as dep
from uuid import UUID
from sqlalchemy.orm import Session
import app.models as models


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
        working_user: models.User = Depends(dep.get_working_user),
        checking_user: models.User = Depends(dep.get_checking_user),
        deposit_collecting_user: models.User = Depends(dep.get_deposit_receiving_user),
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    if working_user.id == checking_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Working and checking volunteer cannot be the same!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    return crud.create_contract(
        contract_data=contract_data,
        working_user_id=working_user.id,
        checking_user_id=checking_user.id,
        deposit_collecting_user_id=deposit_collecting_user.id,
        db=db)

# TODO: returns

