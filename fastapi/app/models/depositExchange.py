from datetime import datetime, date
from uuid import uuid4

from sqlalchemy import UUID, text, ForeignKey, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class DepositExchange(Base):
    __tablename__ = "depositexchanges"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    # NULL means money was taken from bank account
    fromUserId: Mapped[UUID] = mapped_column("fromuserid", ForeignKey("users.id"), nullable=True, quote=False)
    fromUser: Mapped["User"] = relationship("User", foreign_keys=[fromUserId])

    # NULL means money was deposited into the bank account
    toUserId: Mapped[UUID] = mapped_column("touserid", ForeignKey("users.id"), nullable=True, quote=False)
    toUser: Mapped["User"] = relationship("User", foreign_keys=[toUserId])

    amount: Mapped[int] = mapped_column("amount", Integer, nullable=False, quote=False)
    date: Mapped[date] = mapped_column("date", Date, default=datetime.utcnow().date(), server_default=text("(current_date at time zone 'utc')"), nullable=False, quote=False)

    def equal_to_dict(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.fromUserId) == str(other.get("fromUserId")),
            str(self.toUserId) == str(other.get("toUserId")),
            self.amount == other.get("amount"),
            self.date == datetime.strptime(other.get("date"), "%Y-%m-%d").date()
        ])

    def __eq__(self, other):
        if type(other) is dict:
            return self.equal_to_dict(other)
        else:
            return all([
                self.id == other.id,
                self.fromUserId == other.fromUserId,
                self.toUserId == other.toUserId,
                self.amount == other.amount,
                self.date == other.date
            ])
