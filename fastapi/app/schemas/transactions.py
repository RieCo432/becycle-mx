from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List

from app import schemas


class TransactionLineBase(BaseModel):
    amount: int
    accountId: UUID
    
class TransactionLineCreate(TransactionLineBase):
    pass


class TransactionLine(TransactionLineBase):
    id: UUID
    transactionHeaderId: UUID
    
    
class TransactionHeaderBase(BaseModel):
    event: str
    
    
class TransactionHeaderCreate(TransactionHeaderBase):
    pass

class TransactionHeader(TransactionHeaderBase):
    id: UUID
    createdOn: datetime
    createdByUser: schemas.User
    postedOn: datetime | None = None
    postedByUser: schemas.User | None = None
    transactionLines: List[TransactionLine] = []
    
    
class TransactionCreate(BaseModel):
    transactionHeader: TransactionHeaderCreate
    transactionLines: List[TransactionLineCreate]
    