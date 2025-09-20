from typing import List
from uuid import uuid4

from sqlalchemy import UUID, text, String, Text, Identity, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models import bike_colour_association_table


class Colour(Base):
    __tablename__ = "colours"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, nullable=False, default=0,
                                     server_default="0", index=True, quote=False)
    name: Mapped[str] = mapped_column("name", String(50), nullable=False, quote=False)

    bikes: Mapped[List["Bike"]] = relationship(secondary=bike_colour_association_table,
                                                 back_populates="colours")

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.name) == str(other.get("name"))
        ])