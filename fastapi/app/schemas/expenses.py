from pydantic import BaseModel, ConfigDict
from .user import User
from datetime import date
from uuid import UUID


class ExpenseTag(BaseModel):
    id: str
    description: str
    active: bool

class ExpenseBase(BaseModel):
    amount: float
    type: str
    notes: str
    expenseDate: date
    tagId: str

class ExpenseTagUpdate(BaseModel):
    description: str | None = None
    active: bool | None = None

class Expense(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    expenseUser: User
    treasurerUser: User | None
    transferDate: date | None
    id: UUID
    receiptContentType: str
    tag: ExpenseTag

class ExpenseUpdate(BaseModel):
    amount: float | None = None
    type: str | None = None
    notes: str | None = None
    expenseDate: date | None = None
    tagId: str | None = None
    expenseUserId: UUID | None = None
    transferred: bool | None = None
    treasurerUserId: UUID | None = None
    transferDate: date | None = None
