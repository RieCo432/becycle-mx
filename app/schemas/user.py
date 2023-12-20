from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    admin: bool
    depositBearer: bool
    rentalChecker: bool
    appointmentManager: bool
    treasurer: bool
    softDeleted: bool


class UserCreate(UserBase):
    password_cleartext: str
    pin_cleartext: str | None = None
    pass


class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True