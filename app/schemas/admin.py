from pydantic import BaseModel, ConfigDict
from .client import Client
from uuid import UUID


class DetectedPotentialClientDuplicates(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    similarityScore: int
    checked: bool
    client1: Client
    client2: Client
