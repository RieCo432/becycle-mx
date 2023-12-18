from uuid import UUID
from pydantic import BaseModel


class ClientBase(BaseModel):
    firstName: str
    lastName: str
    emailAddress: str


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: UUID

    class Config:
        orm_mode = True
