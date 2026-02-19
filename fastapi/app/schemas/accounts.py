from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List
from .user import User
from .group import Group


class Project(BaseModel):
    id: str
    description: str
    active: bool

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
    restrictedToProjectId: str | None = None

class Account(AccountCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ownerUser: User | None = None
    ownerGroup: Group | None = None
    closedOn: datetime | None = None
    closedByUser: User | None = None
    balance: int
    normalisedBalance: int
    restrictedToProject: Project | None = None
    
class AccountUpdate(AccountBase):
    pass