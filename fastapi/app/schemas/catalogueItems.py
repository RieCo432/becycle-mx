from datetime import datetime, date
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict
from typing import List


class CatalogueItemBase(BaseModel):
    name: str
    description: str
    
    
class CatalogueItemCreate(CatalogueItemBase):
    purchasePrice: int | None = None
    recommendedRetailPrice: int | None = None
    
    
class CatalogueItem(CatalogueItemCreate):
    id: UUID
    catalogueItemPhotoId: UUID | None = None
    available: bool = True
    createdOn: datetime
    
    
class CatalogueItemUpdate(CatalogueItemBase):
    pass
    