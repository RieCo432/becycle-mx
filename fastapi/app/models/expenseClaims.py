import os
from datetime import datetime, date
from typing import List
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base
from .expense import ExpenseReceipt


class ExpenseClaim(Base):
    __tablename__ = "expenseclaims"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    expenseDate: Mapped[date] = mapped_column("expensedate", Date, nullable=False, quote=False)
    
    expenseTransactionHeaderId: Mapped[UUID] = mapped_column("expensetransactionheaderid", ForeignKey("transactionheaders.id"), nullable=False, quote=False)
    expenseTransactionHeader: Mapped["TransactionHeader"] = relationship("TransactionHeader", foreign_keys=[expenseTransactionHeaderId])
    
    reimbursementTransactionHeaderId: Mapped[UUID] = mapped_column("reimbursementtransactionheaderid", ForeignKey("transactionheaders.id"), nullable=True, default=None, server_default=text("NULL"), quote=False)
    reimbursementTransactionHeader: Mapped["TransactionHeader"] = relationship("TransactionHeader", foreign_keys=[reimbursementTransactionHeaderId])

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    receiptFileId: Mapped[UUID] = mapped_column("receiptfileid", ForeignKey("expenseReceipts.id"), nullable=False,
                                                default=None, server_default=text("NULL"), quote=False)
    receiptFile: Mapped[ExpenseReceipt] = relationship(ExpenseReceipt, foreign_keys=[receiptFileId])

    receiptContentType: Mapped[str] = mapped_column("receiptcontenttype", Text, nullable=False, quote=False)