from uuid import UUID
from pydantic import BaseModel
from datetime import date


class ContractBase(BaseModel):
    clientId: UUID
    bikeId: UUID
    workingUserId: UUID
    checkingUserId: UUID
    depositCollectingUserId: UUID

    depositAmountCollected: int

    conditionOfBike: str
    contractType: str
    notes: str | None = None



class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id: UUID

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
