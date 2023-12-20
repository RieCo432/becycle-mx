from uuid import UUID
from pydantic import BaseModel


class BikeBase(BaseModel):
    make: str
    model: str
    colour: str
    decals: str
    serialNumber: str


class BikeCreate(BikeBase):
    pass


class Bike(BikeBase):
    id: UUID

    class Config:
        orm_mode = True
