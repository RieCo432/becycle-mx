from datetime import datetime
import os
from uuid import UUID

from sqlalchemy import select

import app.models as models
import app.schemas as schemas
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status


async def create_expense(db: Session, expense_user: models.User, expense_data: schemas.ExpenseCreate, receipt_file: UploadFile) -> models.Expense:
    new_expense_receipt = models.ExpenseReceipt(
        content = await receipt_file.read(),
    )

    db.add(new_expense_receipt)
    db.commit()

    new_expense = models.Expense(
        type=expense_data.type,
        notes=expense_data.notes,
        expenseUserId=expense_user.id,
        expenseDate=expense_data.expenseDate,
        receiptContentType=receipt_file.content_type,
        amount=expense_data.amount,
        receiptFileId=new_expense_receipt.id
    )
    db.add(new_expense)
    db.commit()

    return new_expense


def get_expense_receipt_file(db: Session, expense_id: UUID) -> dict[str, str]:
    expense = db.scalar(
        select(models.Expense)
        .where(models.Expense.id == expense_id)
    )

    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    output_file_path = os.path.join(data_dir, "tempExpenseReceipt")

    with open(output_file_path, "wb") as fout:
        fout.write(expense.receiptFile.content)

    return {"path": output_file_path, "media_type": expense.receiptContentType}


def patch_expense_transferred(db: Session, expense_id: UUID, treasurer_user: models.User) -> models.Expense:
    expense = db.scalar(
        select(models.Expense)
        .where(
            (models.Expense.transferDate == None)
            & (models.Expense.id == expense_id)
        )
    )

    if expense is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This expense does not exist or has already been transferred"})

    expense.treasurerUserId = treasurer_user.id
    expense.transferDate = datetime.utcnow().date()

    db.commit()

    return expense


def get_expenses(db: Session) -> list[models.Expense]:
    return [
        _ for _ in db.scalars(select(models.Expense))
    ]
