from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import List

from .transactions import TransactionHeader
from .user import User
from .accounts import Account
from .catalogueItems import CatalogueItem
from .bike import Bike


class CatalogueItemSaleLineCreate(BaseModel):
    saleHeaderId: UUID
    catalogueItemId: UUID
    quantity: int
    salePrice: int
    
    
class CatalogueItemSaleLine(CatalogueItemSaleLineCreate):
    id: UUID
    catalogueItem: CatalogueItem
    
    
class CatalogueItemSaleLineUpdate(BaseModel):
    quantity: int
    salePrice: int
    
    
class BikeSaleLineCreate(BaseModel):
    saleHeaderId: UUID
    bikeId: UUID
    salePrice: int
    
    
class BikeSaleLine(BikeSaleLineCreate):
    id: UUID
    bike: Bike


class SaleHeaderBase(BaseModel):
    pass


class SaleHeader(SaleHeaderBase):
    id: UUID
    createdOn: datetime
    createdByUser: User
    
    transactionHeaderId: UUID | None = None
    transactionHeader: TransactionHeader | None = None
    
    catalogueItemSaleLines: List[CatalogueItemSaleLine] = []
    bikeSaleLines: List[BikeSaleLine] = []