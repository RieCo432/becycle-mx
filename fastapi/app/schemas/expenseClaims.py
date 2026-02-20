from pydantic import BaseModel, ConfigDict
from .user import User
from datetime import date
from uuid import UUID
from .transactions import TransactionHeader

class ExpenseClaimBase(BaseModel):
    expenseTransactionHeaderId: UUID
    notes: str | None = None
    expenseDate: date
    
    
class ExpenseClaimCreate(ExpenseClaimBase):
    pass

class ExpenseClaim(ExpenseClaimBase):
    id: UUID
    receiptContentType: str
    expenseTransactionHeader: TransactionHeader
    reimbursementTransactionHeaderId: UUID | None = None
    reimbursementTransactionHeader: TransactionHeader | None = None