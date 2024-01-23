from sqlalchemy import select, func
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
import bcrypt
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def get_user(username: str, db: Session) -> models.User | None:
    if username is None:
        return None
    return db.scalar(
        select(models.User)
        .where(func.lower(models.User.username) == username.lower())
    )


def authenticate_user(username: str, password_cleartext: str, db: Session) -> models.User | None:
    user = get_user(username=username, db=db)
    if user is None:
        return None
    if not bcrypt.checkpw(password_cleartext, user.password):
        return None
    else:
        return user


def validate_user_signature(username: str, password_or_pin, db: Session) -> models.User | None:
    user = get_user(username=username, db=db)
    if user is None:
        return None
    if bcrypt.checkpw(password_or_pin, user.password):
        return user
    if user.pin is None:
        return None
    if bcrypt.checkpw(password_or_pin, user.pin):
        return user

    return None


def create_user(user_data: schemas.UserCreate, db: Session) -> models.User:
    user = models.User(
        username=user_data.username,
        password=bcrypt.hashpw(user_data.password_cleartext, bcrypt.gensalt()),
        pin=bcrypt.hashpw(user_data.pin_cleartext, bcrypt.gensalt()) if user_data.pin_cleartext is not None else None,
        admin=user_data.admin,
        depositBearer=user_data.depositBearer,
        appointmentManager=user_data.appointmentManager,
        rentalChecker=user_data.rentalChecker,
        treasurer=user_data.treasurer
    )
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity Error: Does this user already exist?"
        )
    return user


def get_deposit_bearers(db: Session) -> list[models.User]:
    deposit_bearers = [_ for _ in db.scalars(
        select(models.User)
        .where(
            models.User.depositBearer
            & (~models.User.softDeleted)
        )
    )]

    return deposit_bearers


def get_rental_checkers(db: Session) -> list[models.User]:
    rental_checkers = [_ for _ in db.scalars(
        select(models.User)
        .where(
            models.User.rentalChecker
            & (~models.User.softDeleted)
        )
    )]

    return rental_checkers


def get_active_users(db: Session) -> list[models.User]:
    active_users = [_ for _ in db.scalars(
        select(models.User)
        .where(
            ~models.User.softDeleted
        )
    )]

    return active_users
