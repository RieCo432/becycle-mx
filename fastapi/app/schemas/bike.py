from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .contract import Contract
from .colours import Colour
from app.extensions.disposition import Disposition


class BikeBase(BaseModel):
    make: str
    model: str
    colour: str = None
    colours: list[Colour] | None = None
    decals: str | None = None
    serialNumber: str
    rfidTagSerialNumber: str | None = None
    disposition: Disposition = Disposition.RENTAL


class BikeCreate(BikeBase):
    pass


class Bike(BikeBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class BikeExtended(Bike):
    model_config = ConfigDict(from_attributes=True)

    contracts: list[Contract]
