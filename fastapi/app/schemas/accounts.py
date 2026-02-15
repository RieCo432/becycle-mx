from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List
from .user import User
from .group import Group

class AccountBase(BaseModel):
    name: str
    description: str
    scheduledClosureDate: datetime | None = None
    showInUis: List[str]


class AccountCreate(AccountBase):
    ownerUserId: UUID | None
    ownerGroupId: UUID | None
    type: str
    isInternal: bool

class Account(AccountCreate):
    id: UUID
    ownerUser: User | None = None
    ownerGroup: Group | None = None
    closedOn: datetime | None = None
    closedByUser: User | None = None
    
class AccountUpdate(AccountBase):
    pass