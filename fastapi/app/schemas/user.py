from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from .group import Group


class UserBase(BaseModel):
    username: str
    rentalChecker: bool = False


class UserCreate(UserBase):
    password_cleartext: str
    pin_cleartext: str | None = None


class User(UserBase):
    id: UUID
    softDeleted: bool
    lastAuthenticated: datetime | None = None
    groups: list[Group] = []

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    passwordCleartext: str | None = None
    pinCleartext: str | None = None
    rentalChecker: bool | None = None
    softDeleted: bool | None = None

    def roles_change(self):
        return self.rentalChecker is not None or self.softDeleted is not None


class UserPresentationCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    bio: str
    photoContentType: str | None = None
