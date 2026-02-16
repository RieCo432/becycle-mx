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
                        db: Session = Depends(dep.get_db)) -> list[schemas.Contract]:
    return crud.get_contracts(db=db, open=open, closed=closed, expired=expired)


@contracts.post("/contracts")
async def create_contract(
        contract_data: schemas.ContractCreate,
        email_tasks: BackgroundTasks,
        working_user: models.User = Depends(dep.get_working_user),
        checking_user: models.User = Depends(dep.get_checking_user),
        deposit_collecting_user: models.User = Depends(dep.get_deposit_receiving_user),
        db: Session = Depends(dep.get_db)) -> schemas.Contract:

    raise HTTPException(status_code=status.HTTP_410_GONE, detail={"description": "This endpoint is deprecated."})


@contracts.get("/contracts/drafts")
async def get_contract_drafts(db: Session = Depends(dep.get_db)) -> list[schemas.ContractDraft]:
    return crud.get_contract_drafts(db=db)


@contracts.get("/contracts/drafts/{contract_draft_id}")
async def get_contract_draft(contract_draft_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.ContractDraft:
    return crud.get_contract_draft(db=db, contract_draft_id=contract_draft_id)


@contracts.post("/contracts/drafts")
async def new_contract_draft(
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:

    contract = crud.start_new_contract(db=db)

    return contract


@contracts.put("/contracts/drafts/{contract_draft_id}/client")
async def update_contract_draft_client(
        contract_draft_id: UUID,
        client_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_client(db=db, contract_draft_id=contract_draft_id, client_id=client_id)


@contracts.put("/contracts/drafts/{contract_draft_id}/bike")
async def update_contract_draft_bike(
        contract_draft_id: UUID,
        bike_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_bike(db=db, contract_draft_id=contract_draft_id, bike_id=bike_id)


@contracts.put("/contracts/drafts/{contract_draft_id}/details")
async def update_contract_draft_details(
        contract_draft_id: UUID,
        contract_draft_details: schemas.ContractDraftDetails,
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_details(db=db, contract_draft_id=contract_draft_id, contract_draft_details=contract_draft_details)


@contracts.put("/contracts/drafts/{contract_draft_id}/deposit")
async def update_contract_draft_deposit(
        contract_draft_id: UUID,
        deposit_collected_transaction_header_id: Annotated[UUID, Body(embed=True)],
        deposit_collecting_user: models.User = Depends(dep.get_deposit_receiving_user),
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    crud.post_transaction_header(db=db, transaction_header_id=deposit_collected_transaction_header_id, user=deposit_collecting_user)
    return crud.update_contract_draft_deposit(db=db, contract_draft_id=contract_draft_id, deposit_collected_transaction_header_id=deposit_collected_transaction_header_id)


@contracts.put("/contracts/drafts/{contract_draft_id}/working-user")
async def update_contract_draft_working_user(
        contract_draft_id: UUID,
        working_user: models.User = Depends(dep.get_working_user),
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_working_user(db=db, contract_draft_id=contract_draft_id, working_user=working_user)


@contracts.put("/contracts/drafts/{contract_draft_id}/checking-user")
async def update_contract_draft_checking_user(
        contract_draft_id: UUID,
        checking_user: models.User = Depends(dep.get_checking_user),
        db: Session = Depends(dep.get_db)
) -> schemas.ContractDraft:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if crud.is_checking_user_same_as_working_user(db=db, contract_draft_id=contract_draft_id, checking_user=checking_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Checking user cannot be the same as working user!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return crud.update_contract_draft_checking_user(db=db, contract_draft_id=contract_draft_id,
                                                    checking_user=checking_user)


@contracts.post("/contracts/drafts/{contract_draft_id}/submit")
async def submit_contract(
        contract_draft_id: UUID,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)
) -> schemas.Contract:
    if not crud.does_contract_draft_exist(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract draft not found."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if crud.does_contract_exist_already(db=db, contract_draft_id=contract_draft_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"description": "Contract already exists!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    contract = crud.submit_contract(db=db, contract_draft_id=contract_draft_id)

    email_tasks.add_task(contract.send_creation_email)

    return contract


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
    # TODO: deposit information needs to use new model
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"description": "This endpoint has not been implemented yet."})
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
