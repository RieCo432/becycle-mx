from pydantic import BaseModel, ConfigDict
from .client import ClientExtended
from uuid import UUID


class DetectedPotentialClientDuplicates(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    similarityScore: int
    ignore: bool
    client1: ClientExtended
    client2: ClientExtended
