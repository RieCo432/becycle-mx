import os
from datetime import datetime, date
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    expenseUserId: Mapped[UUID] = mapped_column("expenseUserId", ForeignKey("users.id"), nullable=False)
    expenseUser: Mapped["User"] = relationship("User", foreign_keys=[expenseUserId], back_populates="expenses")

    treasurerUserId: Mapped[UUID] = mapped_column("treasurerUserId", ForeignKey("users.id"), nullable=True, default=None, server_default=text("NULL"))
    treasurerUser: Mapped["User"] = relationship("User", foreign_keys=[treasurerUserId], back_populates="transfers")

    expenseDate: Mapped[date] = mapped_column("expenseDate", Date, nullable=False, quote=False)
    transferDate: Mapped[date] = mapped_column("transferDate", Date, nullable=True, quote=False, server_default=text("NULL"), default=None)

    amount: Mapped[int] = mapped_column("amount", Integer, nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    receiptFile: Mapped[bytes] = mapped_column("receiptFile", LargeBinary, nullable=False, quote=False)
    receiptContentType: Mapped[str] = mapped_column("receiptContentType", Text, nullable=False, quote=False)