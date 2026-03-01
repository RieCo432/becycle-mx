from uuid import UUID

from fastapi import HTTPException
from starlette import status

import app.models as models
import app.schemas as schemas
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from .transactions import get_transaction_header
from ..services.accounts_helpers import AccountTypes


def get_sale_headers(db: Session) -> list[models.SaleHeader]:
    return [_ for _ in db.scalars(
        select(models.SaleHeader)
    )]



def create_sale_header(db: Session, user: models.User) -> models.SaleHeader:
    sale_header = models.SaleHeader(
        createdOn=datetime.now(timezone.utc),
        createdByUserId=user.id
    )
    
    db.add(sale_header)
    
    db.commit()

    return sale_header


def get_sale_header(db: Session, sale_header_id: UUID) -> models.SaleHeader:
    sale_header =  db.scalar(
        select(models.SaleHeader)
        .where(models.SaleHeader.id == sale_header_id)
    )

    if sale_header is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Sale header not found"})
    
    return sale_header



def add_catalogue_item_sale_line(db: Session, catalogue_item_sale_line_data: schemas.CatalogueItemSaleLineCreate) -> models.CatalogueItemSaleLine:
    sale_header = get_sale_header(db=db, sale_header_id=catalogue_item_sale_line_data.saleHeaderId)
    
    catalogue_item_sale_line = models.CatalogueItemSaleLine(
        saleHeaderId=sale_header.id,
        catalogueItemId=catalogue_item_sale_line_data.catalogueItemId,
        quantity=catalogue_item_sale_line_data.quantity,
        salePrice=catalogue_item_sale_line_data.salePrice
    )
    
    db.add(catalogue_item_sale_line)
    db.commit()
    
    return catalogue_item_sale_line


def add_bike_sale_line(db: Session, bike_sale_line_data: schemas.BikeSaleLineCreate) -> models.BikeSaleLine:
    sale_header = get_sale_header(db=db, sale_header_id=bike_sale_line_data.saleHeaderId)
    
    bike_sale_line = models.BikeSaleLine(
        saleHeaderId=sale_header.id,
        bikeId=bike_sale_line_data.bikeId,
        salePrice=bike_sale_line_data.salePrice
    )
    
    db.add(bike_sale_line)
    db.commit()
    
    return bike_sale_line


def does_payment_cover_sale_price(db: Session, transaction_header_id: UUID, sale_header_id: UUID) -> bool:
    transaction_header = get_transaction_header(db=db, transaction_header_id=transaction_header_id)
    sale_header = get_sale_header(db=db, sale_header_id=sale_header_id)
    
    total_sale_price = (sum([line.salePrice for line in sale_header.catalogueItemSaleLines]) 
                        + sum([line.salePrice for line in sale_header.bikeSaleLines]))
    transaction_amount = sum([line.amount for line in transaction_header.transactionLines if line.account.type == AccountTypes.ASSET])
    
    return total_sale_price == transaction_amount


def finalise_sale(db: Session, sale_header_id: UUID, transaction_header_id: UUID) -> models.SaleHeader:
    sale_header = get_sale_header(db=db, sale_header_id=sale_header_id)
    transaction_header = get_transaction_header(db=db, transaction_header_id=transaction_header_id)
    
    if transaction_header is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Transaction header not found"})
    
    if transaction_header.postedOn is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Sale must be posted before it can be finalised"})
    
    sale_header.transactionHeaderId = transaction_header.id    
    
    db.commit()
    return sale_header