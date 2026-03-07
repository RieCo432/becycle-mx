from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session

import app.dependencies as dep
from app import models, schemas, crud

sales = APIRouter(
    tags=["sales"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.check_permissions)]
)


@sales.get("/sales", response_model=list[schemas.SaleHeader])
async def get_sale_headers(
        pending: bool = False,
        db: Session = Depends(dep.get_db)) -> list[schemas.SaleHeader]:
    return crud.get_sale_headers(db, pending=pending)


@sales.post("/sales", response_model=schemas.SaleHeader)
async def create_sale_headers(db: Session = Depends(dep.get_db), user: models.User = Depends(dep.get_current_active_user)) -> schemas.SaleHeader:
    return crud.create_sale_header(db=db, user=user)


@sales.post("/sales/catalogue-item-sale-line", response_model=schemas.CatalogueItemSaleLine)
async def create_catalogue_item_sale_line(
        catalogue_item_sale_line: schemas.CatalogueItemSaleLineCreate, 
        db: Session = Depends(dep.get_db)
) -> schemas.CatalogueItemSaleLine:
    return crud.add_catalogue_item_sale_line(db=db, catalogue_item_sale_line_data=catalogue_item_sale_line)


@sales.put("/sales/catalogue-item-sale-line/{catalogue_item_sale_line_id}", response_model=schemas.CatalogueItemSaleLine)
async def update_catalogue_item_sale_line(
        catalogue_item_sale_line_id: UUID,
        catalogue_item_sale_line_update: schemas.CatalogueItemSaleLineUpdate,
        db: Session = Depends(dep.get_db)
) -> schemas.CatalogueItemSaleLine:
    return crud.update_catalogue_item_sale_line(db=db, catalogue_item_sale_line_id=catalogue_item_sale_line_id, catalogue_item_sale_line_update=catalogue_item_sale_line_update)


@sales.delete("/sales/catalogue-item-sale-line/{catalogue_item_sale_line_id}", response_model=None)
async def delete_catalogue_item_sale_line(
        catalogue_item_sale_line_id: UUID,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.delete_catalogue_item_sale_line(db=db, catalogue_item_sale_line_id=catalogue_item_sale_line_id)


@sales.post("/sales/bike-sale-line", response_model=schemas.BikeSaleLine)
async def create_bike_sale_line(
        bike_sale_line: schemas.BikeSaleLineCreate, 
        db: Session = Depends(dep.get_db)
) -> schemas.BikeSaleLine:
    return crud.add_bike_sale_line(db=db, bike_sale_line_data=bike_sale_line)


@sales.put("/sales/bike-sale-line/{bike_sale_line_id}")
async def update_bike_sale_line(
        bike_sale_line_id: UUID,
        bike_sale_line: schemas.BikeSaleLineUpdate,
        db: Session = Depends(dep.get_db)
) -> schemas.BikeSaleLine:
    return crud.update_bike_sale_line(db=db, bike_sale_line_id=bike_sale_line_id, bike_sale_line_update=bike_sale_line)


@sales.delete("/sales/bike-sale-line/{bike_sale_line_id}")
async def delete_bike_sale_line(
        bike_sale_line_id: UUID,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.delete_bike_sale_line(db=db, bike_sale_line_id=bike_sale_line_id)


@sales.patch("/sales/{sale_header_id}/payment")
async def finalise_sale(
        sale_header_id: UUID,
        transaction_header_id: Annotated[UUID, Body(embed=True)],
        user: models.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.SaleHeader:
    # TODO: make sure sale is not complete already
    if not crud.does_payment_cover_sale_price(db=db, transaction_header_id=transaction_header_id, sale_header_id=sale_header_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Sale price does not cover payment."}
        )
    
    crud.post_transaction_header(db=db, transaction_header_id=transaction_header_id, user=user)
    return crud.finalise_sale(db=db, sale_header_id=sale_header_id, transaction_header_id=transaction_header_id)