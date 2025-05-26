import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app import auth
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


users_public = APIRouter(
    tags=["users-public"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@users_public.post("/public/users/token", response_model=schemas.Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(dep.get_db)):
    if form_data.password == "password":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Cannot login with default password. Please contact an admin to set a password!"})
    user = crud.authenticate_user(username=form_data.username, password_cleartext=form_data.password, db=db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Incorrect username or password"})

    access_token = auth.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}