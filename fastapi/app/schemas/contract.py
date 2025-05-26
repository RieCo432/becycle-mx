from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContractBase(BaseModel):
    clientId: UUID
    bikeId: UUID

    depositAmountCollected: int

    conditionOfBike: str
    contractType: str
    notes: str | None = None


class ContractCreate(ContractBase):
    pass



class ContractPublic(ContractBase):
    id: UUID

    startDate: date
    endDate: date

    returnedDate: date | None = None
    depositAmountReturned: int | None = None
    detailsSent: bool = False
    expiryReminderSent: bool = False
    returnDetailsSent: bool = False


class Contract(ContractPublic):
    workingUserId: UUID
    checkingUserId: UUID
    depositCollectingUserId: UUID

    returnAcceptingUserId: UUID | None = None
    depositReturningUserId: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractDraftDetails(BaseModel):
    conditionOfBike: str
    contractType: str
    notes: str | None = None


class ContractRestricted(ContractPublic):
    workingUsername: str
    checkingUsername: str
    depositCollectingUsername: str

    returnAcceptingUsername: str | None = None
    depositReturningUsername: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractPatch(BaseModel):
    depositAmountCollected: int
    conditionOfBike: str
    notes: str | None = None
    contractType: str
    startDate: date
    endDate: date
    returnedDate: date | None = None
    returned: bool
    depositAmountReturned: int | None = None
    workingUserId: UUID
    checkingUserId: UUID
    depositCollectingUserId: UUID
    returnAcceptingUserId: UUID | None = None
    depositReturningUserId: UUID | None = None
