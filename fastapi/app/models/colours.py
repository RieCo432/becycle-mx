from typing import List, Any
from uuid import uuid4

from sqlalchemy import UUID, text, String, Text, Identity, Integer, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
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

    @hybrid_property
    def hex(self) -> str:
        """Convert the integer ID to a 6-character hex string."""
        return f"#{self.id:06X}"

    @hex.expression
    def hex(cls):
        # This allows querying: session.query(Colour).filter(Colour.hex == "FF0000")
        from sqlalchemy import func
        return func.concat("#", func.upper(func.lpad(func.to_hex(cls.id), 6, '0')))

    @staticmethod
    def getintvalue(hex_value: str)-> int:
        return int(hex_value.lstrip('#'), 16)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.name) == str(other.get("name"))
        ])