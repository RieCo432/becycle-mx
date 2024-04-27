from pydantic import BaseModel, ConfigDict
from .user import User
from datetime import date
from uuid import UUID


class ExpenseCreate(BaseModel):
    amount: int
    type: str
    notes: str
    expenseDate: date


class Expense(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)
    expenseUser: User
    treasurerUser: User | None
    transferDate: date | None
    id: UUID
    receiptContentType: str



