from datetime import date

from fastapi import APIRouter, Depends, UploadFile, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from typing import Annotated

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
import app.models as models

from uuid import UUID

expenses = APIRouter(
    tags=["expenses"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@expenses.post("/expenses")
async def post_expense(
        expense_type: Annotated[str, Body(embed=True)],
        amount: Annotated[float, Body(embed=True)],
        notes: Annotated[str, Body(embed=True)],
        expense_date: Annotated[date, Body(embed=True)],
        receipt_file: UploadFile,
        expense_user: schemas.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Expense:
    return crud.create_expense(db=db, expense_user=expense_user, expense_data=schemas.ExpenseCreate(
        type=expense_type,
        amount=amount,
        notes=notes,
        expenseDate=expense_date
    ), receipt_file=receipt_file)


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
        db: Session = Depends(dep.get_db)
) -> list[schemas.Expense]:
    return crud.get_expenses(db=db)


@expenses.patch("/expenses/{expense_id}/transfer")
async def patch_expense_transferred(
        expense_id: UUID,
        db: Session = Depends(dep.get_db),
        treasurer_user: models.User = Depends(dep.get_current_treasurer_user)
) -> schemas.Expense:
    return crud.patch_expense_transferred(db=db, expense_id=expense_id, treasurer_user=treasurer_user)
