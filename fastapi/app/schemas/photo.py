from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Photo(BaseModel):
    id: UUID
    createdOn: datetime
    userId: UUID
    contentType: str
    