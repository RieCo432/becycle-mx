from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
import app.schemas as schemas
import app.crud as crud
import app.dependencies as dep
from uuid import UUID
from sqlalchemy.orm import Session
import app.models as models
from typing import Annotated


contracts = APIRouter(
    tags=["contracts"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@contracts.get("/contracts/{contract_id}/", dependencies=[Depends(dep.get_current_active_user)])
async def get_contract(contract_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Contract:
    return crud.get_contract(db=db, contract_id=contract_id)


@contracts.get("/contracts")
async def get_contracts(open: bool = True,
                        closed: bool = True,
                        expired: bool = True,
                        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, open=open, closed=closed, expired=expired)


@contracts.post("/contract", dependencies=[Depends(dep.get_current_active_user)])
async def create_contract(
        contract_data: schemas.ContractCreate,
        email_tasks: BackgroundTasks,
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

    contract = crud.create_contract(
        contract_data=contract_data,
        working_user_id=working_user.id,
        checking_user_id=checking_user.id,
        deposit_collecting_user_id=deposit_collecting_user.id,
        db=db)

    email_tasks.add_task(contract.send_creation_email)

    return contract


@contracts.patch("/contracts/{contract_id}/return")
async def return_bike(
        contract_id: UUID,
        email_tasks: BackgroundTasks,
        deposit_amount_returned: Annotated[int, Body()],
        working_user: models.User = Depends(dep.get_working_user),
        deposit_returning_user: models.User = Depends(dep.get_deposit_returning_user),
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    if deposit_amount_returned > deposit_returning_user.get_deposit_bearer_balance():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "This deposit bearer does not have enough funds!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    contract = crud.return_contract(db=db,
                                    contract_id=contract_id,
                                    deposit_amount_returned=deposit_amount_returned,
                                    return_accepting_user_id=working_user.id,
                                    deposit_returning_user_id=deposit_returning_user.id)

    email_tasks.add_task(contract.send_return_email)

    return contract


@contracts.patch("/contracts/{contract_id}/extend", dependencies=[Depends(dep.get_current_active_user)])
async def extend_contract(
        contract_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    contract = crud.extend_contract(db=db, contract_id=contract_id)

    email_tasks.add_task(contract.send_creation_email)
    
    return contract


@contracts.get("/contract/types", dependencies=[Depends(dep.get_current_active_user)])
async def get_contract_types() -> list[str]:
    return ["standard", "refugee", "child", "premium"]


@contracts.get("/contracts/paper", dependencies=[Depends(dep.get_current_admin_user)])
async def get_paper_contract(paper_id: str, db: Session = Depends(dep.get_db)) -> UUID:
    return crud.get_paper_contract(db=db, paper_id=paper_id)


@contracts.get("/contracts/paper/suggestions", dependencies=[Depends(dep.get_current_active_user)])
async def get_paper_contract_suggestions(old_id: str | None = None, db: Session = Depends(dep.get_db)) -> list[str]:
    if old_id is not None:
        return crud.get_paper_contract_suggestions(db=db, old_id=old_id)
    else:
        return []

