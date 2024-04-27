import os
from uuid import UUID

from sqlalchemy import select

import app.models as models
import app.schemas as schemas
from sqlalchemy.orm import Session
from fastapi import UploadFile


async def create_expense(db: Session, expense_user: models.User, expense_data: schemas.ExpenseCreate, receipt_file: UploadFile) -> models.Expense:
    new_expense = models.Expense(
        notes=expense_data.notes,
        expenseUserId=expense_user.id,
        expenseDate=expense_data.expenseDate,
        receiptFile=await receipt_file.read(),
        receiptContentType=receipt_file.content_type,
        amount=expense_data.amount,
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
        fout.write(expense.receiptFile)

    return {"path": output_file_path, "media_type": expense.receiptContentType}

