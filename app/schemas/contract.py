from uuid import UUID
from pydantic import BaseModel


class ContractBase(BaseModel):
    clientId: UUID


class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id: UUID

    class Config:
        orm_mode = True
