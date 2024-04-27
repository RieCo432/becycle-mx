from datetime import date

from fastapi import APIRouter, Depends, UploadFile, Body
from sqlalchemy.orm import Session

from typing import Annotated

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

expenses = APIRouter(
    tags=["expenses"],
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
    responses={404: {"description": "Not Found"}}
)


@expenses.post("/expenses")
async def post_expense(
        amount: Annotated[int, Body(embed=True)],
        notes: Annotated[str, Body(embed=True)],
        expense_date: Annotated[date, Body(embed=True)],
        receipt_file: UploadFile,
        expense_user: schemas.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.Expense:
    return await crud.create_expense(db=db, expense_user=expense_user, expense_data=schemas.ExpenseCreate(
        amount=amount,
        notes=notes,
        expenseDate=expense_date
    ), receipt_file=receipt_file)