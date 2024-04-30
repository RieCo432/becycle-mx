from typing import List
from uuid import uuid4

from sqlalchemy import String, UUID, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Bike(Base):
    __tablename__ = "bikes"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    make: Mapped[str] = mapped_column("make", String(40), nullable=False, quote=False)
    model: Mapped[str] = mapped_column("model", String(40), nullable=False, quote=False)
    colour: Mapped[str] = mapped_column("colour", String(40), nullable=False, quote=False)
    decals: Mapped[str] = mapped_column("decals", String(40), nullable=True, quote=False)
    serialNumber: Mapped[str] = mapped_column("serialNumber", String(40), nullable=False, quote=False)

    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="bike")
