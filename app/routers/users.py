from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated
import app.models as models
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
import os
from app import auth


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


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


@users.get("/users/", dependencies=[Depends(dep.get_current_admin_user)])
async def get_users(db: Session = Depends(dep.get_db)) -> list[schemas.User]:
    return crud.get_users(db=db)


@users.get("/users/{user_id}/", dependencies=[Depends(dep.get_current_active_user)])
async def get_user(user_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.User:
    return crud.get_user(db=db, user_id=user_id)


@users.patch("/users/{user_id}/", dependencies=[Depends(dep.get_current_admin_user)])
async def patch_user(user_id: UUID,
                     updated_user_data: schemas.UserUpdate,
                     db: Session = Depends(dep.get_db)) -> schemas.User:
    user = crud.get_user(db=db, user_id=user_id)
    return crud.update_user(db=db,
                            user=user,
                            updated_user_data=updated_user_data)


@users.get("/users/me/deposit_balance")
async def get_my_deposit_balance(
        current_user: Annotated[models.User, Depends(dep.get_current_deposit_bearer_user)]
) -> int:
    return current_user.get_deposit_bearer_balance()


@users.post("/user/check/password")
async def post_user_password_check(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)
) -> bool:
    user = crud.authenticate_user(db=db, username=form_data.username, password_cleartext=form_data.password)

    return user is not None


@users.post("/user/check/password-or-pin")
async def post_user_password_or_pin_check(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)
) -> bool:
    user = crud.validate_user_signature(db=db, username=form_data.username, password_or_pin=form_data.password)

    return user is not None


@users.post("/user", dependencies=[Depends(dep.get_current_admin_user)])
async def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(dep.get_db),
) -> schemas.User:
    created_user = crud.create_user(user_data=user_data, db=db)
    return created_user


@users.get("/users/active-users", dependencies=[Depends(dep.get_current_active_user)])
async def get_active_users(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    active_users = crud.get_active_users(db=db)
    return active_users


@users.get("/users/deposit-bearers", dependencies=[Depends(dep.get_current_active_user)])
async def get_deposit_bearers(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    deposit_bearers = crud.get_deposit_bearers(db=db)
    return deposit_bearers


@users.get("/users/rental-checkers", dependencies=[Depends(dep.get_current_active_user)])
async def get_rental_checkers(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    rental_checkers = crud.get_rental_checkers(db=db)
    return rental_checkers

