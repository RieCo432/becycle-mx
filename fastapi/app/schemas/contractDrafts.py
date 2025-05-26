from datetime import date
from uuid import UUID

from pydantic import BaseModel
from .client import ClientBase
from .bike import BikeBase
from .user import UserBase


class ContractDraft(BaseModel):
    id: UUID
    clientId: UUID | None = None
    client: ClientBase | None = None
    bikeId: UUID | None = None
    bike: BikeBase | None = None
    conditionOfBike: str | None = None
    contractType: str | None = None
    notes: str | None = None
    startDate: date
    endDate: date
    workingUserId: UUID | None = None
    workingUser: UserBase | None = None
    checkingUserId: UUID | None = None
    checkingUser: UserBase | None = None
    depositCollectingUserId: UUID | None = None
    depositCollectingUser: UserBase | None = None
    depositAmountCollected: int | None = None