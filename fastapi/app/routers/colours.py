from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

colours = APIRouter(
    tags=["colours"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@colours.get("/colours")
async def get_colours(db: Session = Depends(dep.get_db)) -> list[schemas.Colour]:
    return crud.get_colours(db=db)