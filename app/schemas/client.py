from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .appointments import Appointment
from .contract import Contract


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


class ClientExtended(Client):
    model_config = ConfigDict(from_attributes=True)

    appointments: list[Appointment]
    contracts: list[Contract]


class ClientChangeName(BaseModel):
    firstName: str
    lastName: str
