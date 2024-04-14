from uuid import UUID
from pydantic import BaseModel, ConfigDict
from .contract import Contract


class BikeBase(BaseModel):
    make: str
    model: str
    colour: str
    decals: str | None = None
    serialNumber: str


class BikeCreate(BikeBase):
    pass


class Bike(BikeBase):
    id: UUID

    class Config:
        orm_mode = True


class BikeExtended(Bike):
    model_config = ConfigDict(from_attributes=True)

    contracts: list[Contract]
