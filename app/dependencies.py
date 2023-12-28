from jose import jwt, JWTError
from app.database.db import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Body
import app.models as models
import app.crud as crud
from sqlalchemy.orm import Session
from app.config import SECRET_KEY, ALGORITHM
import app.schemas as schemas
from uuid import UUID


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
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.UserTokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_client(token: Annotated[str, Depends(client_oauth2_scheme)], db: Session = Depends(get_db)) -> models.Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
            detail="Soft-deleted User",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_appointment_manager_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.appointmentManager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Appointment manager privileges are required for this action!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


async def get_current_admin_user(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required for this action!",
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
            detail="Working User wrong password or pin",
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
            detail="Checking User wrong password or pin",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return checking_user


async def get_deposit_collecting_user(
        deposit_collecting_username: str = Body("deposit_collecting_username"),
        deposit_collecting_user_password: str = Body("deposit_collecting_user_password"),
        db: Session = Depends(get_db)) -> models.User:
    deposit_collecting_user = crud.authenticate_user(username=deposit_collecting_username, password_cleartext=deposit_collecting_user_password, db=db)
    if deposit_collecting_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit collecting user wrong password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return deposit_collecting_user
