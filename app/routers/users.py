from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated
import app.models as models


users = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@users.get("/users/me")
async def get_user_me(
        current_user: Annotated[models.User, Depends(dep.get_current_active_user)]
) -> schemas.User:
    return current_user


@users.post("/user", dependencies=[Depends(dep.get_current_admin_user)])
async def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(dep.get_db),
) -> schemas.User:
    created_user = crud.create_user(user_data=user_data, db=db)
    return created_user
