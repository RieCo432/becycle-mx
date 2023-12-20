from datetime import timedelta
from fastapi import APIRouter, Depends
import app.crud as crud
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
import app.schemas as schemas
from app import auth
import app.dependencies as dep


login = APIRouter(
    tags=["token"],
    dependencies=[Depends(dep.get_db)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}}
)


@login.post("/token", response_model=schemas.Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(dep.get_db)):
    user = crud.authenticate_user(username=form_data.username, password_cleartext=form_data.password, db=db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    if user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user has been soft-deleted")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

