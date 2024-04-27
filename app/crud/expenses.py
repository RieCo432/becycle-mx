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
