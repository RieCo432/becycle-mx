from typing import List
from uuid import uuid4

from datetime import datetime
from sqlalchemy import String, UUID, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Bike(Base):
    __tablename__ = "bikes"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    make: Mapped[str] = mapped_column("make", String(40), nullable=False, quote=False)
    model: Mapped[str] = mapped_column("model", String(40), nullable=False, quote=False)
    colour: Mapped[str] = mapped_column("colour", String(40), nullable=False, quote=False)
    decals: Mapped[str] = mapped_column("decals", String(40), nullable=True, quote=False)
    serialNumber: Mapped[str] = mapped_column("serialnumber", String(40), nullable=False, quote=False)
    rfidTagSerialNumber: Mapped[str] = mapped_column("rfidtagserialnumber", String(24), nullable=True, quote=False)
    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)


    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="bike")

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.make) == str(other.get("make", None)),
            str(self.model) == str(other.get("model", None)),
            str(self.colour) == str(other.get("colour", None)),
            str(self.decals) == str(other.get("decals", None)),
            str(self.serialNumber) == str(other.get("serialNumber", None)),
            str(self.rfidTagSerialNumber) == str(other.get("rfidTagSerialNumber", None)),
            str(self.createdOn) == str(other.get("createdOn", None))
        ])
