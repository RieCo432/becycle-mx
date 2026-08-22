from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas


photos = APIRouter(
    tags=["photos"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)

@photos.get("/photos")
async def get_photos(
        db: Session = Depends(dep.get_db)
) -> List[schemas.Photo]:
    return crud.get_photos(db=db)


@photos.delete("/photos/{photo_id}")
async def delete_photo(
        photo_id: UUID,
        db: Session = Depends(dep.get_db)
) -> None:
    crud.delete_photo(db=db, photo_id=photo_id)


@photos.get("/photos/{photo_id}")
async def get_photo(
        photo_id: UUID,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    photo = crud.get_photo(db=db, photo_id=photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail={"description": "Photo not found"})
    return FileResponse(**crud.get_file_response(photo.content, photo.contentType))


@photos.get("/photos/{photo_id}/thumbnail")
async def get_photo_thumbnail(
        photo_id: UUID,
        db: Session = Depends(dep.get_db)
) -> FileResponse:
    photo = crud.get_photo(db=db, photo_id=photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail={"description": "Photo not found"})
    return FileResponse(**crud.get_file_response(photo.thumbnail, photo.contentType))


@photos.post("/photos")
async def post_photos(
        uploaded_photos: list[UploadFile],
        user: schemas.User = Depends(dep.get_current_user),
        db: Session = Depends(dep.get_db)
) -> list[schemas.Photo]:

    return crud.create_photos(db=db, photos=uploaded_photos, user=user)