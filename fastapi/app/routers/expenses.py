from datetime import date
from fastapi import APIRouter, Depends, UploadFile, Body, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Annotated, List
from starlette import status
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
import app.models as models
from uuid import UUID

expenses = APIRouter(
    tags=["expenses"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@expenses.post("/expenses")
async def post_expense(
        amount: Annotated[float, Body(embed=True)],
        expense_type: Annotated[str, Body(embed=True)],
        notes: Annotated[str, Body(embed=True)],
        expense_date: Annotated[date, Body(embed=True)],
        tag_id: Annotated[str, Body(embed=True)],
        receipt_file: UploadFile,
        expense_user: schemas.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Expense:
    expense_data = schemas.ExpenseBase(
        amount=amount,
        type=expense_type,
        tagId=tag_id,
        expenseDate=expense_date,
        notes=notes,
    )

    if crud.does_expense_exist(db=db, expense_user=expense_user, expense_data=expense_data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"description": "This appears to be a duplicate expense. Please contact a system admin if this is a mistake."}
        )
    return crud.create_expense(db=db, expense_user=expense_user, expense_data=expense_data, receipt_file=receipt_file)


@expenses.post("/expenses/claims")
async def post_expense_claim(
        notes: Annotated[str, Body(embed=True)],
        expense_date: Annotated[date, Body(embed=True)],
        expense_claim_transaction_header_id: Annotated[UUID, Body(embed=True)],
        receipt_file: UploadFile,
        user: schemas.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)) -> schemas.ExpenseClaim:
    
    expense_claim_data = schemas.ExpenseClaimCreate(notes=notes, expenseTransactionHeaderId=expense_claim_transaction_header_id, expenseDate=expense_date)
    
    crud.post_transaction_header(db=db, transaction_header_id=expense_claim_data.expenseTransactionHeaderId, user=user)
    
    return crud.create_expense_claim(db=db, expense_claim_data=expense_claim_data, receipt_file=receipt_file)


@expenses.get("/expenses/{expense_id}/receipt")
async def get_expense_receipt(
        expense_id: UUID,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    return FileResponse(**crud.get_expense_receipt_file(db=db, expense_id=expense_id))


@expenses.get("/expenses/types")
async def get_expense_types(db: Session = Depends(dep.get_db)) -> list[schemas.ExpenseType]:
    return crud.get_expense_types(db=db)


@expenses.get("/expenses")
async def get_expenses(
        tag: str | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.Expense]:
    return crud.get_expenses(db=db, tag_id=tag)


@expenses.delete("/expenses/{expense_id}")
async def delete_expense(
        expense_id: UUID,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.delete_expense(db=db, expense_id=expense_id)


@expenses.patch("/expenses/{expense_id}/transfer")
async def patch_expense_transferred(
        expense_id: UUID,
        db: Session = Depends(dep.get_db),
        user: models.User = Depends(dep.get_current_active_user)
) -> schemas.Expense:
    return crud.patch_expense_transferred(db=db, expense_id=expense_id, treasurer_user=user)


@expenses.patch("/expenses/{expense_id}")
async def patch_expense(
        updated_expense_data: schemas.ExpenseUpdate,
        expense_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.Expense:
    return crud.update_expense(db=db, expense_id=expense_id, updated_expense_data=updated_expense_data)


@expenses.get("/expenses/tags")
async def get_expense_tags(
        inactive: bool = False,
        db: Session = Depends(dep.get_db)) -> List[schemas.ExpenseTag]:
    return crud.get_expense_tags(db=db, inactive=inactive)

@expenses.post("/expenses/tags")
async def post_expense_tag(
        new_expense_tag: schemas.ExpenseTag,
        db: Session = Depends(dep.get_db)) -> schemas.ExpenseTag:
    return crud.create_expense_tag(db=db, expense_tag=new_expense_tag)

@expenses.patch("/expenses/tags/{expense_tag_id}")
async def patch_expense_tag(
        expense_tag_id: str,
        expense_tag_update: schemas.ExpenseTagUpdate,
        db: Session = Depends(dep.get_db)
) -> schemas.ExpenseTag:
    return crud.update_expense_tag(db=db, expense_tag_id=expense_tag_id, expense_tag_update=expense_tag_update)

@expenses.get("/expenses/all-receipts")
async def get_all_expenses_and_receipts(
        start_date: date,
        end_date: date,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    return FileResponse(**crud.get_all_expenses_and_receipts(db=db, start_date=start_date, end_date=end_date))
