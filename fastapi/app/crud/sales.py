from uuid import UUID

from fastapi import HTTPException
from starlette import status

import app.models as models
import app.schemas as schemas
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from datetime import datetime, timezone
from .transactions import get_transaction_header
from ..services.accounts_helpers import AccountTypes


def get_sale_headers(db: Session, pending: bool = True, completed: bool = True) -> list[models.SaleHeader]:
    query = select(models.SaleHeader)
    
    filters = []
    
    if pending:
        filters.append(models.SaleHeader.transactionHeaderId == None)
    if completed:
        filters.append(models.SaleHeader.transactionHeaderId != None)
    
    return [_ for _ in db.scalars(
        query.where(or_(*filters))
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
    
    if sale_header.transactionHeaderId is not None:
        for line in transaction_header.transactionLines:
            db.delete(line)
        db.flush()
        db.delete(transaction_header)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Sale has already been finalised. New transaction has been deleted."})
    
    sale_header.transactionHeaderId = transaction_header.id    
    
    db.commit()
    return sale_header


def get_catalogue_item_sale_line(db: Session, catalogue_item_sale_line_id: UUID) -> models.CatalogueItemSaleLine:
    catalogue_item_sale_line =  db.scalar(
        select(models.CatalogueItemSaleLine)
        .where(models.CatalogueItemSaleLine.id == catalogue_item_sale_line_id)
    )
    return catalogue_item_sale_line


def get_bike_sale_line(db: Session, bike_sale_line_id: UUID) -> models.BikeSaleLine:
    bike_sale_line =  db.scalar(
        select(models.BikeSaleLine)
        .where(models.BikeSaleLine.id == bike_sale_line_id)
    )
    return bike_sale_line

def update_catalogue_item_sale_line(db: Session, catalogue_item_sale_line_id: UUID, catalogue_item_sale_line_update: schemas.CatalogueItemSaleLineUpdate) -> models.CatalogueItemSaleLine:
    catalogue_item_sale_line = get_catalogue_item_sale_line(db=db, catalogue_item_sale_line_id=catalogue_item_sale_line_id)
    
    if catalogue_item_sale_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Catalogue item sale line not found"})

    sale_header = catalogue_item_sale_line.saleHeader
    if sale_header.transactionHeaderId is not None and sale_header.transactionHeader.postedOn is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Sale header is already posted."}
        )
    
    catalogue_item_sale_line.salePrice = catalogue_item_sale_line_update.salePrice
    catalogue_item_sale_line.quantity = catalogue_item_sale_line_update.quantity
    
    db.commit()
    
    return catalogue_item_sale_line


def update_bike_sale_line(db: Session, bike_sale_line_id: UUID, bike_sale_line_update: schemas.BikeSaleLineUpdate) -> models.BikeSaleLine:
    bike_sale_line = get_bike_sale_line(db=db, bike_sale_line_id=bike_sale_line_id)

    if bike_sale_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Bike sale line not found"})

    sale_header = bike_sale_line.saleHeader
    if sale_header.transactionHeaderId is not None and sale_header.transactionHeader.postedOn is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Sale header is already posted."}
        )

    bike_sale_line.salePrice = bike_sale_line_update.salePrice

    db.commit()

    return bike_sale_line


def delete_catalogue_item_sale_line(db: Session, catalogue_item_sale_line_id: UUID) -> None:
    catalogue_item_sale_line = get_catalogue_item_sale_line(db=db, catalogue_item_sale_line_id=catalogue_item_sale_line_id)

    sale_header = catalogue_item_sale_line.saleHeader
    if sale_header.transactionHeaderId is not None and sale_header.transactionHeader.postedOn is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Sale header is already posted."}
        )
    
    if catalogue_item_sale_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Catalogue item sale line not found"})
    
    db.delete(catalogue_item_sale_line)
    db.commit()
    
    
def delete_bike_sale_line(db: Session, bike_sale_line_id: UUID) -> None:
    bike_sale_line = get_bike_sale_line(db=db, bike_sale_line_id=bike_sale_line_id)
    
    sale_header = bike_sale_line.saleHeader
    if sale_header.transactionHeaderId is not None and sale_header.transactionHeader.postedOn is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Sale header is already posted."}
        )
    
    if bike_sale_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Bike sale line not found"})
    
    db.delete(bike_sale_line)
    db.commit()
    
    
def delete_sale_header(db: Session, sale_header_id: UUID) -> None:
    sale_header = get_sale_header(db=db, sale_header_id=sale_header_id)
    
    if sale_header.transactionHeaderId is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Closed sales cannot be deleted."}
        )
    
    try:
        for line in sale_header.catalogueItemSaleLines:
            db.delete(line)
        for line in sale_header.bikeSaleLines:
            db.delete(line)
        db.delete(sale_header)
        db.flush()
        
        db.delete(sale_header)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Sale header could not be deleted."})
        