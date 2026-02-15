import __future__
import decimal
from typing import List
from uuid import uuid4

from datetime import datetime
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Boolean, ARRAY, Float, Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class TransactionHeader(Base):
    __tablename__ = "transactionheaders"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    event: Mapped[str] = mapped_column("event", String(60), nullable=False, quote=False)

    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)
    createdByUserId: Mapped[UUID] = mapped_column("createdbyuserid", ForeignKey("users.id"), nullable=False, quote=False)
    createdByUser: Mapped["User"] = relationship("User", foreign_keys=[createdByUserId], back_populates="transactionsCreated")
    
    transactionLines: Mapped[List["TransactionLine"]] = relationship("TransactionLine", back_populates="transactionHeader")


    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.event) == str(other.get("event", None)),
            str(self.createdOn) == str(other.get("createdOn", None)),
            str(self.createdByUserId) == str(other.get("createdByUserId", None)),
        ])
    
    def does_balance(self) -> bool:
        return sum([transaction_line for transaction_line in self.transactionLines]) == 0
    
    def is_posted(self) -> bool:
        return all([transaction_line.is_posted() for transaction_line in self.transactionLines])
    
class TransactionLine(Base):
    __tablename__ = "transactionlines"
    
    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    transactionHeaderId: Mapped[UUID] = mapped_column("transactionheaderid", ForeignKey("transactionheaders.id"), nullable=False, quote=False)
    transactionHeader: Mapped["TransactionHeader"] = relationship("TransactionHeader", foreign_keys=[transactionHeaderId], back_populates="transactionLines")
    
    accountId: Mapped[UUID] = mapped_column("accountid", ForeignKey("accounts.id"), nullable=False, quote=False)
    account: Mapped["Account"] = relationship("Account", foreign_keys=[accountId], back_populates="transactionLines")
    
    amount: Mapped[int] = mapped_column("amount", Integer, nullable=False, quote=False)  # value in the smallest unit (penny), positive for debit, negative for credit
    
    postedOn: Mapped[datetime] = mapped_column("postedon", DateTime, nullable=True, quote=False)
    postedByUserId: Mapped[UUID] = mapped_column("postedbyuserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    postedByUser: Mapped["User"] = relationship("User", foreign_keys=[postedByUserId], back_populates="transactionsPosted")
    
    
    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.transactionHeaderId) == str(other.get("transactionHeaderId", None)),
            str(self.accountId) == str(other.get("accountId", None)),
            str(self.amount) == str(other.get("amount", None)),
            str(self.postedOn) == str(other.get("postedOn", None)),
            str(self.postedByUserId) == str(other.get("postedByUserId", None)),
        ])
    
    def is_posted(self):
        return self.postedOn is not None
    
    def created_on(self) -> datetime:
        return self.transactionHeader.createdOn
    
    def created_by(self) -> "User":
        return self.transactionHeader.createdByUser
