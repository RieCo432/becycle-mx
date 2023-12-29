from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DepositExchangeBase(BaseModel):
    amount: int


class DepositExchangeCreate(DepositExchangeBase):
    pass


class DepositExchange(DepositExchangeBase):
    id: UUID
    fromUserId: UUID
    toUserId: UUID
    timestamp: datetime
