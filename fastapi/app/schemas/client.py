from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .appointments import Appointment


class ClientBase(BaseModel):
    firstName: str
    lastName: str
    emailAddress: str
    anonymised: bool = False


class ClientCreate(ClientBase):
    pass


class ClientPreAuth(BaseModel):
    id: UUID


class ClientTemp(ClientBase):
    id: UUID
    expirationDateTime: datetime


class Client(ClientBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ContractBrief(BaseModel):
    id: UUID


class ClientExtended(Client):
    model_config = ConfigDict(from_attributes=True)

    appointments: list[Appointment]
    contracts: list[ContractBrief]


class ClientChangeName(BaseModel):
    firstName: str
    lastName: str
