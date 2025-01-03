import os
from datetime import datetime, date
from typing import List
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base


class ExpenseReceipt(Base):
    __tablename__ = "expenseReceipts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    content: Mapped[bytes] = mapped_column("content", LargeBinary, nullable=False, quote=False)


class ExpenseTag(Base):
    __tablename__ = "expensetags"

    id: Mapped[str] = mapped_column("id", String(20), nullable=False, quote=False, primary_key=True)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)
    active: Mapped[bool] = mapped_column("active", Boolean, nullable=False, default=True, server_default=text("TRUE"),
                                         quote=False)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    expenseUserId: Mapped[UUID] = mapped_column("expenseuserid", ForeignKey("users.id"), nullable=False, quote=False)
    expenseUser: Mapped["User"] = relationship("User", foreign_keys=[expenseUserId], back_populates="expenses")

    treasurerUserId: Mapped[UUID] = mapped_column("treasureruserid", ForeignKey("users.id"), nullable=True, default=None, server_default=text("NULL"), quote=False)
    treasurerUser: Mapped["User"] = relationship("User", foreign_keys=[treasurerUserId], back_populates="transfers")

    expenseDate: Mapped[date] = mapped_column("expensedate", Date, nullable=False, quote=False)
    transferDate: Mapped[date] = mapped_column("transferdate", Date, nullable=True, quote=False, server_default=text("NULL"), default=None)

    amount: Mapped[float] = mapped_column("amount", Float, nullable=False, quote=False)

    type: Mapped[str] = mapped_column("type", Text, nullable=False, quote=False)

    tagId: Mapped[str] = mapped_column("tagid", ForeignKey("expensetags.id"), nullable=False, quote=False)
    tag: Mapped[ExpenseTag] = relationship("ExpenseTag", foreign_keys=[tagId])

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    receiptFileId: Mapped[UUID] = mapped_column("receiptfileid", ForeignKey(ExpenseReceipt.id), nullable=True,
                                                  default=None, server_default=text("NULL"), quote=False)
    receiptFile: Mapped[ExpenseReceipt] = relationship(ExpenseReceipt, foreign_keys=[receiptFileId])

    receiptContentType: Mapped[str] = mapped_column("receiptcontenttype", Text, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.expenseUserId) == str(other.get("expenseUser").get("id")),
            (other.get("treasurerUser") is None and self.treasurerUserId is None) or ((other.get("treasurerUser") is not None and self.treasurerUserId is not None) and (str(self.treasurerUserId) == str(other.get("treasurerUser").get("id")))),
            self.expenseDate.strftime("%Y-%m-%d") == str(other.get("expenseDate")),
            other.get("transferDate") is None if self.transferDate is None else self.transferDate.strftime("%Y-%m-%d") == str(other.get("transferDate")),
            self.amount == other.get("amount"),
            str(self.type) == str(other.get("type")),
            str(self.notes) == str(other.get("notes")),
            str(self.receiptContentType) == str(other.get("receiptContentType")),
        ])
