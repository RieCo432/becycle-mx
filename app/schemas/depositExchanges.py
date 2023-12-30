from pydantic import BaseModel
from datetime import date
from uuid import UUID


class DepositExchangeBase(BaseModel):
    amount: int


class DepositExchangeCreate(DepositExchangeBase):
    pass


class DepositExchange(DepositExchangeBase):
    id: UUID
    fromUserId: UUID
    toUserId: UUID
    date: date
