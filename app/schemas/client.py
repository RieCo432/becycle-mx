from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class ClientBase(BaseModel):
    firstName: str
    lastName: str
    emailAddress: str


class ClientCreate(ClientBase):
    pass


class ClientPreAuth(BaseModel):
    id: UUID


class ClientTemp(ClientBase):
    id: UUID
    expirationDateTime: datetime


class Client(ClientBase):
    id: UUID

    class Config:
        orm_mode = True


class ClientChangeName(BaseModel):
    firstName: str
    lastName: str
