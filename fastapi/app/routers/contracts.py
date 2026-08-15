from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

contracts = APIRouter(
    tags=["contracts"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@contracts.get("/contracts")
async def get_contracts(open: bool = True,
                        closed: bool = True,
                        expired: bool = True,
                        draft: bool = False,
                        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, open=open, closed=closed, expired=expired, draft=draft)


@contracts.post("/contracts")
async def new_contract(
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:

    contract = crud.start_new_contract(db=db)

    return contract


@contracts.get("/contracts/drafts/{contract_id}")
async def get_contract_draft(contract_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Contract:
    return crud.get_contract_draft(db=db, contract_id=contract_id)


@contracts.put("/contracts/drafts/{contract_id}/client")
async def update_contract_draft_client(
        contract_id: UUID,
        client_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    return crud.update_contract_draft_client(db=db, contract_id=contract_draft.id, client_id=client_id)


@contracts.put("/contracts/drafts/{contract_id}/bike")
async def update_contract_draft_bike(
        contract_id: UUID,
        bike_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    return crud.update_contract_draft_bike(db=db, contract_id=contract_draft.id, bike_id=bike_id)


@contracts.put("/contracts/drafts/{contract_id}/details")
async def update_contract_draft_details(
        contract_id: UUID,
        contract_details: schemas.ContractDetails,
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    return crud.update_contract_draft_details(db=db, contract_id=contract_draft.id, contract_details=contract_details)


@contracts.put("/contracts/drafts/{contract_id}/deposit")
async def update_contract_draft_deposit(
        contract_id: UUID,
        deposit_collected_transaction_header_id: Annotated[UUID, Body(embed=True)],
        deposit_collecting_user: models.User = Depends(dep.get_deposit_receiving_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    # crud.post_transaction_header(db=db, transaction_header_id=deposit_collected_transaction_header_id, user=deposit_collecting_user)
    return crud.update_contract_draft_deposit(db=db, contract_id=contract_id, deposit_collected_transaction_header_id=deposit_collected_transaction_header_id)


@contracts.put("/contracts/drafts/{contract_id}/working-user")
async def update_contract_draft_working_user(
        contract_id: UUID,
        working_user: models.User = Depends(dep.get_working_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    return crud.update_contract_draft_working_user(db=db, contract_draft_id=contract_draft.id, working_user=working_user)


@contracts.put("/contracts/drafts/{contract_id}/checking-user")
async def update_contract_draft_checking_user(
        contract_id: UUID,
        checking_user: models.User = Depends(dep.get_checking_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    if crud.is_checking_user_same_as_working_user(db=db, contract_draft_id=contract_id, checking_user=checking_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Checking user cannot be the same as working user!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_checking_user(db=db, contract_id=contract_draft.id,
                                                    checking_user=checking_user)


@contracts.patch("/contracts/drafts/{contract_id}/submit")
async def submit_contract(
        contract_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    contract_draft = crud.get_contract_draft(db=db, contract_id=contract_id)
    if crud.does_contract_exist_already(db=db, contract_id=contract_draft.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"description": "Contract already exists!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    contract = crud.submit_contract(db=db, contract_id=contract_id)

    email_tasks.add_task(contract.send_creation_email)

    return contract_draft


@contracts.get("/contracts/types")
async def get_contract_types(db: Session = Depends(dep.get_db)) -> list[schemas.ContractType]:
    return crud.get_contract_types(db=db)


@contracts.get("/contracts/paper")
async def get_paper_contract(paper_id: str, db: Session = Depends(dep.get_db)) -> UUID:
    return crud.get_paper_contract(db=db, paper_id=paper_id)


@contracts.get("/contracts/paper/suggestions")
async def get_paper_contract_suggestions(old_id: str | None = None, db: Session = Depends(dep.get_db)) -> list[str]:
    if old_id is not None:
        return crud.get_paper_contract_suggestions(db=db, old_id=old_id)
    else:
        return []


@contracts.get("/contracts/{contract_id}")
async def get_contract(contract_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Contract:
    return crud.get_contract(db=db, contract_id=contract_id)


@contracts.delete("/contracts/{contract_id}")
async def delete_contract(
        contract_id: UUID,
        db: Session = Depends(dep.get_db)):
    # TODO: deposit information needs to use new model
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"description": "This endpoint has not been implemented yet."})
    crud.delete_contract(db=db, contract_id=contract_id)


@contracts.patch("/contracts/{contract_id}")
async def patch_contract(
        contract_id: UUID,
        contract_patch_data: schemas.ContractPatch,
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    return crud.patch_contract_details(db=db, contract_id=contract_id, contract_patch_data=contract_patch_data)


@contracts.patch("/contracts/{contract_id}/return")
async def return_bike(
        contract_id: UUID,
        email_tasks: BackgroundTasks,
        deposit_settled_transaction_header_id: Annotated[UUID, Body()],
        working_user: models.User = Depends(dep.get_working_user),
        deposit_returning_user: models.User = Depends(dep.get_deposit_returning_user),
        db: Session = Depends(dep.get_db)) -> schemas.Contract:


    crime_reports = crud.get_crime_reports(db=db, contract_id=contract_id)
    if len([report for report in crime_reports if report.closedOn is None]) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "You cannot return a contract while there is an open crime report!"})

    # crud.post_transaction_header(db=db, transaction_header_id=deposit_settled_transaction_header_id, user=deposit_returning_user)
    contract = crud.return_contract(db=db,
                                    contract_id=contract_id,
                                    deposit_settled_transaction_header_id=deposit_settled_transaction_header_id,
                                    return_accepting_user_id=working_user.id)

    email_tasks.add_task(contract.send_return_email)

    return contract


@contracts.patch("/contracts/{contract_id}/extend")
async def extend_contract(
        contract_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    contract = crud.extend_contract(db=db, contract_id=contract_id)

    email_tasks.add_task(contract.send_creation_email)
    
    return contract
