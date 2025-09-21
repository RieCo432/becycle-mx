from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .contract import Contract
from .colours import Colour


class BikeBase(BaseModel):
    make: str
    model: str
    colour: str = ""
    colours: list[Colour] = []
    decals: str | None = None
    serialNumber: str
    rfidTagSerialNumber: str | None = None


class BikeCreate(BikeBase):
    pass


class Bike(BikeBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class BikeExtended(Bike):
    model_config = ConfigDict(from_attributes=True)

    contracts: list[Contract]
