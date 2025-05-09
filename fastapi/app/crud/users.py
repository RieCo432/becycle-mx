import os
from datetime import datetime
from uuid import UUID

import bcrypt
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_user_by_username(username: str, db: Session) -> models.User | None:
    if username is None:
        return None
    return db.scalar(
        select(models.User)
        .where(func.lower(models.User.username) == username.lower())
    )


def get_user(db: Session, user_id: UUID) -> models.User | None:
    return db.scalar(
        select(models.User)
        .where(models.User.id == user_id)
    )


def authenticate_user(username: str, password_cleartext: str, db: Session) -> models.User | None:
    user = get_user_by_username(username=username, db=db)
    if not _is_user_active(user):
        return None
    if _validate_password_or_pin(password_cleartext, user.password):
        user.lastAuthenticated = datetime.utcnow()
        db.commit()
        return user
    return None

def validate_user_signature(username: str, password_or_pin, db: Session) -> models.User | None:
    user = get_user_by_username(username=username, db=db)
    if not _is_user_active(user):
        return None
    if (_validate_password_or_pin(password_or_pin, user.password) or
        _validate_password_or_pin(password_or_pin, user.pin)):
        user.lastAuthenticated = datetime.utcnow()
        db.commit()
        return user

    return None

def _is_user_active(user):
    if user is None:
        return False
    if user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User has been soft-deleted"})
    return True




def _validate_password_or_pin(password_or_pin, actual):
    if (actual is None):
        return False
    return bcrypt.checkpw(password_or_pin, actual)

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
            detail={"description": "Integrity Error: Does this user already exist?"}
        )
    return user


def get_deposit_bearers(db: Session) -> list[models.User]:
    deposit_bearers = [_ for _ in db.scalars(
        select(models.User)
        .where(
            models.User.depositBearer
            & (~models.User.softDeleted)
        )
        .order_by(func.lower(models.User.username))
    )]

    return deposit_bearers


def get_rental_checkers(db: Session) -> list[models.User]:
    rental_checkers = [_ for _ in db.scalars(
        select(models.User)
        .where(
            models.User.rentalChecker
            & (~models.User.softDeleted)
        )
        .order_by(func.lower(models.User.username))
    )]

    return rental_checkers


def get_active_users(db: Session) -> list[models.User]:
    active_users = [_ for _ in db.scalars(
        select(models.User)
        .where(
            ~models.User.softDeleted
        )
        .order_by(func.lower(models.User.username))
    )]

    return active_users


def update_user(db: Session, user: models.User,
                updated_user_data: schemas.UserUpdate) -> models.User:
    if updated_user_data.passwordCleartext is not None:
        user.password = bcrypt.hashpw(updated_user_data.passwordCleartext, bcrypt.gensalt())
    if updated_user_data.pinCleartext is not None:
        user.pin = bcrypt.hashpw(updated_user_data.pinCleartext, bcrypt.gensalt())
    if updated_user_data.admin is not None:
        user.admin = updated_user_data.admin
    if updated_user_data.depositBearer is not None:
        user.depositBearer = updated_user_data.depositBearer
    if updated_user_data.rentalChecker is not None:
        user.rentalChecker = updated_user_data.rentalChecker
    if updated_user_data.appointmentManager is not None:
        user.appointmentManager = updated_user_data.appointmentManager
    if updated_user_data.treasurer is not None:
        user.treasurer = updated_user_data.treasurer
    if updated_user_data.softDeleted is not None:
        user.softDeleted = updated_user_data.softDeleted

    db.commit()

    return user


def get_users(db: Session) -> list[models.User]:
    return [_ for _ in db.scalars(
        select(models.User)
    )]


def update_or_create_user_presentation_card(db: Session, user: models.User, name: str, bio: str, photo: UploadFile | None) -> models.UserPresentationCard:
    user_photo = None
    if photo is not None:
        from PIL import Image
        current_dir = os.path.dirname(__file__)
        temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
        temp_image_path = os.path.join(temp_data_dir, photo.filename)

        with Image.open(photo.file) as image:
            width = image.size[0]
            height = image.size[1]

            if width != height:
                shorter = width if width < height else height
                image = image.crop((
                    (width - shorter) // 2,
                    (height - shorter) // 2,
                    (width + (width - shorter) // 2),
                    (height - (height - shorter) // 2)
                ))

            if image.size[0] > 1024:
                image = image.resize((1024, 1024))

            with open(temp_image_path, "wb") as fout:
                image.save(fout)

        with open(temp_image_path, "rb") as fin:
            user_photo = models.UserPhoto(
                content=fin.read()
            )
            db.add(user_photo)
            db.commit()

    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.userId == user.id)
    )

    if user_presentation_card is None:
        if user_photo is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No photo provided"})

        user_presentation_card = models.UserPresentationCard(
            userId=user.id,
            name=name,
            bio=bio,
            photoFileId=user_photo.id,
            photoContentType=photo.content_type
        )

        db.add(user_presentation_card)



    else:
        user_presentation_card.name = name
        user_presentation_card.bio = bio

        if user_photo is not None:
            old_user_photo = db.scalar(
                select(models.UserPhoto)
                .where(models.UserPhoto.id == user_presentation_card.photoFileId)
            )

            user_presentation_card.photoFileId = user_photo.id
            user_presentation_card.photoContentType = photo.content_type
            db.delete(old_user_photo)

    db.commit()

    return user_presentation_card


def get_user_presentation_cards(db: Session) -> list[models.UserPresentationCard]:
    return [
        _ for _ in db.scalars(
            select(models.UserPresentationCard)
            .join(models.User)
            .where(models.User.softDeleted == False)
        )
    ]


def get_user_presentation_card_photo(db: Session, card_id: UUID) -> dict[str, str]:
    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == card_id)
    )

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    output_file_path = os.path.join(temp_data_dir, str(card_id))

    with open(output_file_path, "wb") as fout:
        fout.write(user_presentation_card.photoFile.content)

    return {"path": output_file_path, "media_type": user_presentation_card.photoContentType}


def get_user_presentation_card(db: Session, user: models.User) -> models.UserPresentationCard:
    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.userId == user.id)
    )

    if user_presentation_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User Presentation Card not found"})

    return user_presentation_card


def get_user_presentation_card_by_id(db: Session, presentation_card_id: UUID) -> models.UserPresentationCard:
    return db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == presentation_card_id)
    )


def delete_user_presentation_card_by_id(db: Session, presentation_card_id: UUID) -> models.UserPresentationCard:
    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == presentation_card_id)
    )

    db.delete(user_presentation_card)
    db.commit()

    return user_presentation_card


def delete_user_presentation_card(db: Session, user: models.User) -> models.UserPresentationCard:
    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.userId == user.id)
    )

    db.delete(user_presentation_card)
    db.commit()

    return user_presentation_card
