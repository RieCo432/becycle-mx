from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .bike import BikeExtended
from .client import ClientExtended


class DetectedPotentialClientDuplicates(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    similarityScore: int
    ignore: bool
    client1: ClientExtended
    client2: ClientExtended


class DetectedPotentialBikeDuplicates(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    similarityScore: int
    ignore: bool
    bike1: BikeExtended
    bike2: BikeExtended
