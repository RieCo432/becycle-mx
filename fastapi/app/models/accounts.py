from typing import List
from uuid import uuid4

from datetime import datetime, date
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Boolean, ARRAY, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    name: Mapped[str] = mapped_column("name", String(60), nullable=False, quote=False, unique=True)
    description: Mapped[str] = mapped_column("description", String(255), nullable=True, quote=False)

    ownerUserId: Mapped[UUID] = mapped_column("owneruserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    ownerUser: Mapped["User"] = relationship("User", foreign_keys=[ownerUserId], back_populates="accountsOwned")

    ownerGroupId: Mapped[UUID] = mapped_column("ownergroupid", ForeignKey("groups.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    ownerGroup: Mapped["Group"] = relationship("Group", foreign_keys=[ownerGroupId], back_populates="accountsOwned")

    type: Mapped[str] = mapped_column("type", String(20), nullable=False, quote=False)
    isInternal: Mapped[bool] = mapped_column("isinternal", Boolean, nullable=False, quote=False)

    scheduledClosureDate: Mapped[date] = mapped_column("scheduledclosuredate", Date, nullable=True, quote=False)
    
    closedOn: Mapped[datetime] = mapped_column("closedon", DateTime, nullable=True, quote=False)    
    closedByUserId: Mapped[UUID] = mapped_column("closedbyuserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    closedByUser: Mapped["User"] = relationship("User", foreign_keys=[closedByUserId], back_populates="accountsClosed")
    
    showInUis: Mapped[List[str]] = mapped_column("showinuis", ARRAY(String(20)), nullable=False, quote=False, server_default=text("ARRAY[]::text[]"))
    
    transactionLines: Mapped[List["TransactionLine"]] = relationship("TransactionLine", back_populates="account")
    
    def balance(self):
        return sum([line.amount for line in self.transactionLines])
    
    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.name) == str(other.get("name", None)),
            str(self.description) == str(other.get("description", None)),
            str(self.ownerUserId) == str(other.get("ownerUserId", None)),
            str(self.ownerGroupId) == str(other.get("ownerGroupId", None)),
            str(self.type) == str(other.get("type", None)),
            str(self.isInternal) == str(other.get("isInternal", None)),
            str(self.scheduledClosureDate) == str(other.get("scheduledClosureDate", None)),
            str(self.closedOn) == str(other.get("closedOn", None)),
            str(self.closedByUserId) == str(other.get("closedByUserId", None))
        ])