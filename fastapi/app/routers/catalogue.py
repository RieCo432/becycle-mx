from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Body, Form
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import FileResponse

import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

catalogue = APIRouter(
    tags=["catalogue"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)




@catalogue.get("/catalogue", response_model=List[schemas.CatalogueItem])
async def get_catalogue(
        include_unavailable: bool = False,
        db: Session = Depends(dep.get_db)) -> List[schemas.CatalogueItem]:
    return crud.get_catalogue(db, include_unavailable=include_unavailable)



@catalogue.post("/catalogue", response_model=schemas.CatalogueItem)
async def post_catalogue_item(
        name: Annotated[str, Form()],
        description: Annotated[str, Form()],
        purchase_price: Annotated[int | None, Form()] = None,
        recommended_retail_price: Annotated[int | None, Form()] = None,
        photo: UploadFile | None = None,
        db: Session = Depends(dep.get_db)
) -> schemas.CatalogueItem:
    new_catalogue_item = schemas.CatalogueItemCreate(
        name=name,
        description=description, 
        purchasePrice=purchase_price, 
        recommendedRetailPrice=recommended_retail_price)
    return crud.create_catalogue_item(db, new_catalogue_item, photo)


@catalogue.put("/catalogue/{catalogue_item_id}", response_model=schemas.CatalogueItem)
async def patch_catalogue_item(
        catalogue_item_id: UUID,
        name: Annotated[str, Body(embed=True)],
        description: Annotated[str, Body(embed=True)],
        photo: UploadFile | None = None,
        db: Session = Depends(dep.get_db)
) -> schemas.CatalogueItem:
    updated_catalogue_item = schemas.CatalogueItemUpdate(name=name, description=description)
    return crud.update_catalogue_item(db, catalogue_item_id, updated_catalogue_item, photo)


@catalogue.patch("/catalogue/{catalogue_item_id}/availability")
async def patch_make_catalogue_item_available(
        catalogue_item_id: UUID,
        available: Annotated[bool, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.CatalogueItem:
    return crud.set_catalogue_item_available(db, catalogue_item_id, available)


@catalogue.get("/catalogue/{catalogue_item_id}/photo")
async def get_catalogue_item_photo(
        catalogue_item_id: UUID,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    return FileResponse(**crud.get_catalogue_item_photo(db=db, catalogue_item_id=catalogue_item_id))
