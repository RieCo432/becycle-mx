from uuid import UUID
from pydantic import BaseModel


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

    class Config:
        orm_mode = True