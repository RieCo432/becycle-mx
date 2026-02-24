from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List


class CatalogueItemBase(BaseModel):
    name: str
    description: str
    
    
class CatalogueItemCreate(CatalogueItemBase):
    purchasePrice: int | None
    recommendedRetailPrice: int | None
    
    
class CatalogueItem(CatalogueItemCreate):
    id: UUID
    catalogueItemPhotoId: UUID | None = None
    available: bool = True
    createdOn: datetime
    
    
class CatalogueItemUpdate(CatalogueItemBase):
    pass
    