import os
import uuid
from datetime import timezone, datetime
from math import ceil
from uuid import UUID
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
import app.models as models
from typing import List


def get_photos(db: Session) -> List[models.Photo]:
    photos = [_ for _ in db.scalars(
        select(models.Photo)
    )]
    return photos


def get_photo(db: Session, photo_id: UUID) -> models.Photo:
    photo = db.scalar(select(models.Photo).where(models.Photo.id == photo_id))
    if photo is None:
        raise HTTPException(status_code=404, detail={"description": "Photo not found"})
    return photo


def get_file_response(data: bytes, content_type: str) -> dict[str, str]:
    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")

    output_file_path = os.path.join(temp_data_dir, str(uuid.uuid4()))

    with open(output_file_path, "wb") as fout:
        fout.write(data)

    return {"path": output_file_path, "media_type": content_type}


def save_photo(db: Session, photo: UploadFile, user: models.User, auto_commit: bool = True) -> models.Photo:
    if not photo.content_type.startswith("image"):
        raise HTTPException(status_code=400, detail={"description": "Invalid file type"})

    from PIL import Image

    [*base, ext] = photo.filename.split(".")
    thumbnail_file_name = f"{''.join(base)}_thumbnail.{ext}"

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    photo_file_path = os.path.join(temp_data_dir, photo.filename)
    thumbnail_file_path = os.path.join(temp_data_dir, thumbnail_file_name)

    with Image.open(photo.file) as image:
        larger = max(image.size)

        if larger > 4096:
            ratio = int(ceil(larger / 4096))
            image = image.reduce(ratio)

        image.save(photo_file_path)
        
        image.thumbnail((256, 256))
        image.save(thumbnail_file_path)


    content = None
    thumbnail_content = None

    with open(photo_file_path, "rb") as fin:
        content = fin.read()
        
    with open(thumbnail_file_path, "rb") as fin:
        thumbnail_content = fin.read()


    new_contract_photo = models.Photo(
        userId=user.id,
        createdOn=datetime.now(timezone.utc),
        contentType=photo.content_type,
        content=content,
        thumbnail=thumbnail_content,
    )

    db.add(new_contract_photo)
    if auto_commit:
        db.commit()

    return new_contract_photo


def create_photos(db: Session, photos: List[UploadFile], user: models.User) -> List[models.Photo]:
    added_photos = []
    for photo in photos:
        new_photo = save_photo(db=db, photo=photo, user=user, auto_commit=False)
        added_photos.append(new_photo)

    db.commit()
    for photo in added_photos:
        db.refresh(photo)

    return added_photos


def delete_photo(db: Session, photo_id: UUID) -> None:
    photo = get_photo(db=db, photo_id=photo_id)
    db.delete(photo)
    db.commit()
