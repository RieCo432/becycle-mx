from uuid import UUID
from pydantic import BaseModel
from datetime import date


class ContractBase(BaseModel):
    clientId: UUID
    bikeId: UUID

    depositAmountCollected: int

    conditionOfBike: str
    contractType: str
    notes: str | None = None


class ContractCreate(ContractBase):
    pass


class ContractReturn(BaseModel):
    id: UUID
    depositAmountReturned: int


class ContractExtend(BaseModel):
    id: UUID


class Contract(ContractBase):
    id: UUID

    workingUserId: UUID
    checkingUserId: UUID
    depositCollectingUserId: UUID

    startDate: date
    endDate: date
    returnAcceptingUserId: UUID | None = None
    depositReturningUserId: UUID | None = None
    returnedDate: date | None = None
    depositAmountReturned: int | None = None
    detailsSent: bool = False
    expiryReminderSent: bool = False
    returnDetailsSent: bool = False

    class Config:
        orm_mode = True
