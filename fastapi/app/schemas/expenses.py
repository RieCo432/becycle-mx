from symtable import Class

from fastapi import UploadFile
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

class ExpenseCreate(ExpenseBase):
    receiptFile: UploadFile

class Expense(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    expenseUser: User
    treasurerUser: User | None
    transferDate: date | None
    id: UUID
    receiptContentType: str
    tag: ExpenseTag
