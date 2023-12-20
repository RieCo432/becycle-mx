from sqlalchemy import select
from sqlalchemy.orm import Session
import app.models as models
import bcrypt


def get_user(username: str, db: Session) -> models.User | None:
    return db.scalar(
        select(models.User)
        .where(models.User.username == username)
    )


def authenticate_user(username: str, password_cleartext: str, db: Session) -> models.User | None:
    user = get_user(username=username, db=db)
    if user is None:
        return None
    if not bcrypt.checkpw(password_cleartext, user.password):
        return None
    else:
        return user

