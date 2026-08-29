from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List
from .user import User
from .group import Group
from app.services.accounts_helpers import AccountTypes, DashboardDimensions, DashboardIntervals


class Fund(BaseModel):
    id: UUID
    name: str
    description: str
    isActive: bool
    isDefault: bool

class AccountBase(BaseModel):
    name: str
    description: str
    scheduledClosureDate: date | None = None
    showInUis: List[str]


class AccountCreate(AccountBase):
    ownerUserId: UUID | None
    ownerGroupId: UUID | None
    type: str
    isInternal: bool

class Account(AccountCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ownerUser: User | None = None
    ownerGroup: Group | None = None
    closedOn: datetime | None = None
    closedByUser: User | None = None
    balance: int
    normalisedBalance: int
    
class AccountUpdate(AccountBase):
    pass


DashboardAccountsList = list[UUID]
DashboardSeriesQuery = DashboardAccountsList | str


class DashboardDataSeriesMeta(BaseModel):
    flow: str


class DataPoint(BaseModel):
    date: date
    value: int | float
    

class DashboardDataSeries(BaseModel):
    name: str
    meta: DashboardDataSeriesMeta | None = None
    data: list[DataPoint]

class DashboardPart(BaseModel):
    name: str
    series: list[DashboardDataSeries]
    
    
class Dashboard(BaseModel):
    name: str
    parts: list[DashboardPart]



class DashboardPartQuerySeries(BaseModel):
    name: str
    query: DashboardSeriesQuery
    
    
class DashboardPartQueryBase(BaseModel):
    name: str
    series: list[DashboardPartQuerySeries]
    dimension: str
    fundId: UUID | None = None

class DashboardPartMomentQuery(DashboardPartQueryBase):
    mode: str = "moment"
    moment: date
    
class DashboardPartPeriodQuery(DashboardPartQueryBase):
    mode: str = "period"
    startDate: date | None
    endDate: date | None
    interval: str

class DashboardQuery(BaseModel):
    name: str
    queries: list[DashboardPartMomentQuery | DashboardPartPeriodQuery]