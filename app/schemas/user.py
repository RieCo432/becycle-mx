from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    admin: bool = False
    depositBearer: bool = False
    rentalChecker: bool = False
    appointmentManager: bool = False
    treasurer: bool = False


class UserCreate(UserBase):
    password_cleartext: str
    pin_cleartext: str | None = None
    pass


class User(UserBase):
    id: UUID
    softDeleted: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    passwordCleartext: str | None = None
    pinCleartext: str | None = None
    admin: bool | None = None
    depositBearer: bool | None = None
    rentalChecker: bool | None = None
    appointmentManager: bool | None = None
    treasurer: bool | None = None
    softDeleted: bool | None = None

    def roles_change(self):
        return (self.admin is not None or self.depositBearer is not None or self.rentalChecker is not None or
                self.appointmentManager is not None or self.treasurer is not None or self.softDeleted is not None)


class UserPresentationCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    bio: str
    photoContentType: str | None = None
