from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated
import app.models as models
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app import auth


users = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@users.post("/users/token", response_model=schemas.Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(dep.get_db)):
    user = crud.authenticate_user(username=form_data.username, password_cleartext=form_data.password, db=db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    if user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user has been soft-deleted")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


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
