from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models

def get_colours(db : Session) -> list[models.Colour]:
    return [_ for _ in db.scalars(
        select(models.Colour)
    )]