from collections.abc import Callable
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
    dependencies=[Depends(dep.get_db), Depends(dep.get_current_active_user)],
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
    return crud.create_expense(db=db, expense_user=expense_user, expense_data=schemas.ExpenseBase(
        amount=amount,
        type=expense_type,
        tagId=tag_id,
        expenseDate=expense_date,
        notes=notes,
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
        tag: str | None = None,
        db: Session = Depends(dep.get_db)
) -> list[schemas.Expense]:
    return crud.get_expenses(db=db, tag_id=tag)


@expenses.delete("/expenses/{expense_id}")
async def delete_expense(
        expense_id: UUID,
        user: Annotated[models.User, Depends(dep.get_current_admin_user)],
        db: Session = Depends(dep.get_db)
) -> None:
    crud.delete_expense(db=db, expense_id=expense_id)


@expenses.patch("/expenses/{expense_id}/transfer")
async def patch_expense_transferred(
        expense_id: UUID,
        db: Session = Depends(dep.get_db),
        treasurer_user: models.User = Depends(dep.get_current_treasurer_user)
) -> schemas.Expense:
    return crud.patch_expense_transferred(db=db, expense_id=expense_id, treasurer_user=treasurer_user)

@expenses.get("/expenses/tags")
async def get_expense_tags(
        inactive: bool = False,
        db: Session = Depends(dep.get_db)) -> List[schemas.ExpenseTag]:
    return crud.get_expense_tags(db=db, inactive=inactive)

@expenses.post("/expenses/tags", dependencies=[Depends(dep.get_current_admin_user)])
async def post_expense_tag(
        new_expense_tag: schemas.ExpenseTag,
        db: Session = Depends(dep.get_db)) -> schemas.ExpenseTag:
    return crud.create_expense_tag(db=db, expense_tag=new_expense_tag)

@expenses.patch("/expenses/tags/{expense_tag_id}", dependencies=[Depends(dep.get_current_admin_user)])
async def patch_expense_tag(
        expense_tag_id: str,
        expense_tag_update: schemas.ExpenseTagUpdate,
        db: Session = Depends(dep.get_db)
) -> schemas.ExpenseTag:
    return crud.update_expense_tag(db=db, expense_tag_id=expense_tag_id, expense_tag_update=expense_tag_update)
