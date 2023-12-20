from fastapi import APIRouter, Depends
import app.crud as crud
import app.schemas as schemas
from app.dependencies import get_db, get_current_active_user
from sqlalchemy.orm import Session
from typing import Annotated
import app.models as models


users = APIRouter(
    tags=["users"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not Found"}}
)


@users.get("/users/me")
async def get_user_me(
        current_user: Annotated[models.User, Depends(get_current_active_user)]
) -> schemas.User:
    return current_user

