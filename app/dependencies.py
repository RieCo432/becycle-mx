from jose import jwt, JWTError
from app.database.db import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
import app.models as models
import app.crud as crud
from sqlalchemy.orm import Session
from app.config import SECRET_KEY, ALGORITHM
import app.schemas as schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> models.User:
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    if current_user.softDeleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Soft-deleted User",
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
