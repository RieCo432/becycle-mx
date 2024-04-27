import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import app.crud as crud
import app.models as models
import app.schemas as schemas
from app.database.db import SessionLocal

API_SECRET = os.environ['API_SECRET']
API_SECRET_ALGORITHM = os.environ['API_SECRET_ALGORITHM']


user_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="users/token",
    scheme_name="user_oauth2_scheme")

client_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="clients/token",
    scheme_name="client_oauth2_scheme")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: Annotated[str, Depends(user_oauth2_scheme)], db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"description": "Could not validate credentials. Please login again."},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, API_SECRET, algorithms=[API_SECRET_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.UserTokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_client(token: Annotated[str, Depends(client_oauth2_scheme)], db: Session = Depends(get_db)) -> models.Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"description": "Could not validate credentials. Please login again!"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, API_SECRET, algorithms=[API_SECRET_ALGORITHM])
        client_id_str: str = payload.get("sub")
        if client_id_str is None:
            raise credentials_exception
        token_data = schemas.ClientTokenData(client_id=UUID(client_id_str))
    except JWTError:
        raise credentials_exception

    client = crud.get_client(client_id=token_data.client_id, db=db)
    if client is None:
        raise credentials_exception
    return client


async def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    if current_user.softDeleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Soft-deleted User"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_appointment_manager_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.appointmentManager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"description": "Appointment manager privileges are required for this action!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_deposit_bearer_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.depositBearer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"description": "This page can only be viewed by deposit bearers!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_admin_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"description": "Admin privileges are required for this action!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_treasurer_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.treasurer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"description": "Treasurer privileges are required for this action!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_working_user(
        working_username: str = Body("working_username"),
        working_user_password_or_pin: str = Body("working_user_password_or_pin"),
        db: Session = Depends(get_db)) -> models.User:
    working_user = crud.validate_user_signature(username=working_username, password_or_pin=working_user_password_or_pin, db=db)
    if working_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Working User wrong password or pin"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return working_user


async def get_checking_user(
        checking_username: str = Body("checking_username"),
        checking_user_password_or_pin: str = Body("checking_user_password_or_pin"),
        db: Session = Depends(get_db)) -> models.User:
    checking_user = crud.validate_user_signature(username=checking_username, password_or_pin=checking_user_password_or_pin, db=db)
    if checking_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Checking User wrong password or pin"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not checking_user.rentalChecker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Not a rental checker!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return checking_user


async def get_deposit_receiving_user(
        deposit_receiving_username: Annotated[str, Body()],
        deposit_receiving_user_password: Annotated[str, Body()],
        db: Session = Depends(get_db)) -> models.User:
    deposit_receiving_user = crud.authenticate_user(username=deposit_receiving_username, password_cleartext=deposit_receiving_user_password, db=db)
    if deposit_receiving_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit receiving user wrong password"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not deposit_receiving_user.depositBearer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Not a deposit bearer!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return deposit_receiving_user


async def get_deposit_returning_user(
        deposit_returning_username: Annotated[str, Body()],
        deposit_returning_user_password: Annotated[str, Body()],
        db: Session = Depends(get_db)) -> models.User:
    deposit_giving_user = crud.authenticate_user(username=deposit_returning_username, password_cleartext=deposit_returning_user_password, db=db)
    if deposit_giving_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit returning user wrong password"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not deposit_giving_user.depositBearer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Not a deposit bearer!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return deposit_giving_user


async def get_deposit_exchange_to_user(
        deposit_receiving_username: Annotated[str, Body()],
        deposit_receiving_user_password: Annotated[str, Body()],
        db: Session = Depends(get_db)) -> models.User:
    deposit_receiving_user = crud.authenticate_user(username=deposit_receiving_username, password_cleartext=deposit_receiving_user_password, db=db)
    if deposit_receiving_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit receiving user wrong password"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not deposit_receiving_user.depositBearer and not deposit_receiving_user.treasurer and deposit_receiving_user.username != "BANK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Not a deposit bearer, treasurer or BANK!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return deposit_receiving_user


async def get_deposit_exchange_from_user(
        deposit_returning_username: Annotated[str, Body()],
        deposit_returning_user_password: Annotated[str, Body()],
        db: Session = Depends(get_db)) -> models.User:
    deposit_giving_user = crud.authenticate_user(username=deposit_returning_username, password_cleartext=deposit_returning_user_password, db=db)
    if deposit_giving_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit returning user wrong password"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not deposit_giving_user.depositBearer and not deposit_giving_user.treasurer and deposit_giving_user.username != "BANK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Not a deposit bearer, treasurer or BANK!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return deposit_giving_user
