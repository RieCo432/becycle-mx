from datetime import date, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from .transactions import TransactionHeader


class CrimeReportBase(BaseModel):
    crimeNumber: str
    contractId: UUID


class CrimeReportCreate(CrimeReportBase):
    pass

class CrimeReport(CrimeReportBase):
    id: UUID
    createdOn: datetime
    closedOn: datetime | None = None


class ContractBase(BaseModel):
    clientId: UUID
    bikeId: UUID

    conditionOfBike: str
    contractType: str
    notes: str | None = None

    depositTransactionHeaders: List[TransactionHeader] = []


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
    crimeReports: List[CrimeReport] = []


class Contract(ContractPublic):
    workingUserId: UUID
    checkingUserId: UUID

    returnAcceptingUserId: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractDraftDetails(BaseModel):
    conditionOfBike: str
    contractType: str
    notes: str | None = None


class ContractRestricted(ContractPublic):
    workingUsername: str
    checkingUsername: str
    returnAcceptingUsername: str | None = None
    depositAmountCollected: int
    depositAmountReturned: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractPatch(BaseModel):
    conditionOfBike: str
    notes: str | None = None
    contractType: str
    startDate: date
    endDate: date
    returnedDate: date | None = None
    workingUserId: UUID
    checkingUserId: UUID
    returnAcceptingUserId: UUID | None = None
