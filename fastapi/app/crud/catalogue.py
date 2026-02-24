import os
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from starlette import status
from typing import List

import app.models as models
import app.schemas as schemas



def get_catalogue_item(db: Session, catalogue_item_id: UUID) -> models.CatalogueItem:
    catalogue_item = db.scalar(select(models.CatalogueItem).where(models.CatalogueItem.id == catalogue_item_id))
    if catalogue_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")
    return catalogue_item

def get_catalogue(db: Session, include_unavailable: bool = False) -> List[models.CatalogueItem]:
    query = select(models.CatalogueItem)
    if not include_unavailable:
        query = query.where(models.CatalogueItem.available == True)
    
    return [_ for _ in db.scalars(
        query
    )]


def create_catalogue_item(db: Session, catalogue_item: schemas.CatalogueItemCreate, photo) -> models.CatalogueItem:
    catalogue_item_photo = None
    if photo is not None:
        from PIL import Image
        current_dir = os.path.dirname(__file__)
        temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
        temp_image_path = os.path.join(temp_data_dir, photo.filename)

        with Image.open(photo.file) as image:
            width = image.size[0]
            height = image.size[1]

            if width != height:
                shorter = width if width < height else height
                image = image.crop((
                    (width - shorter) // 2,
                    (height - shorter) // 2,
                    (width + (width - shorter) // 2),
                    (height - (height - shorter) // 2)
                ))

            if image.size[0] > 1024:
                image = image.resize((1024, 1024))

            with open(temp_image_path, "wb") as fout:
                image.save(fout)

        with open(temp_image_path, "rb") as fin:
            catalogue_item_photo = models.CatalogueItemPhoto(
                content=fin.read(),
                contentType=photo.content_type
            )
            db.add(catalogue_item_photo)
            # db.refresh(catalogue_item_photo)
            db.flush()
    
    
    db_catalogue_item = models.CatalogueItem(
        name=catalogue_item.name,
        description=catalogue_item.description,
        purchasePrice=catalogue_item.purchasePrice,
        recommendedRetailPrice=catalogue_item.recommendedRetailPrice,
        available=True,
        catalogueItemPhotoId=catalogue_item_photo.id if catalogue_item_photo is not None else None
        
    )
    db.add(db_catalogue_item)
    db.commit()
    db.refresh(db_catalogue_item)
    return db_catalogue_item


def update_catalogue_item(db: Session, catalogue_item_id: UUID, catalogue_item_update_date: schemas.CatalogueItemUpdate, photo: UploadFile | None = None) -> models.CatalogueItem:
    catalogue_item_new_photo = None
    if photo is not None:
        from PIL import Image
        current_dir = os.path.dirname(__file__)
        temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
        temp_image_path = os.path.join(temp_data_dir, photo.filename)

        with Image.open(photo.file) as image:
            width = image.size[0]
            height = image.size[1]

            if width != height:
                shorter = width if width < height else height
                image = image.crop((
                    (width - shorter) // 2,
                    (height - shorter) // 2,
                    (width + (width - shorter) // 2),
                    (height - (height - shorter) // 2)
                ))

            if image.size[0] > 1024:
                image = image.resize((1024, 1024))

            with open(temp_image_path, "wb") as fout:
                image.save(fout)

        with open(temp_image_path, "rb") as fin:
            catalogue_item_new_photo = models.CatalogueItemPhoto(
                content=fin.read(),
                contentType=photo.content_type
            )
            db.add(catalogue_item_new_photo)
            # db.refresh(catalogue_item_new_photo)
            db.flush()
            
            
    catalogue_item = get_catalogue_item(db=db, catalogue_item_id=catalogue_item_id)
    
    if catalogue_item_new_photo is not None:
        catalogue_item.catalogueItemPhotoId = catalogue_item_new_photo.id
    if catalogue_item_update_date.name is not None:
        catalogue_item.name = catalogue_item_update_date.name
    if catalogue_item_update_date.description is not None:
        catalogue_item.description = catalogue_item_update_date.description
        
    db.commit()
    db.refresh(catalogue_item)
    
    return catalogue_item


def get_catalogue_item_photo(db: Session, catalogue_item_id: UUID) -> dict[str, str]:
    catalogue_item = get_catalogue_item(db=db, catalogue_item_id=catalogue_item_id)

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    output_file_path = os.path.join(temp_data_dir, str(catalogue_item_id))

    with open(output_file_path, "wb") as fout:
        fout.write(catalogue_item.catalogueItemPhoto.content)

    return {"path": output_file_path, "media_type": catalogue_item.catalogueItemPhoto.contentType}


def set_catalogue_item_available(db: Session, catalogue_item_id: UUID, available: bool) -> models.CatalogueItem:
    catalogue_item = get_catalogue_item(db=db, catalogue_item_id=catalogue_item_id)
    catalogue_item.available = available
    db.commit()
    db.refresh(catalogue_item)
    
    return catalogue_item