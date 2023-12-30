from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, DateTime
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import CONTRACT_EXPIRE_MONTHS
from app.database.db import Base


class DepositExchange(Base):
    __tablename__ = "depositexchanges"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    fromUserId: Mapped[UUID] = mapped_column("fromUserId", ForeignKey("users.id"), nullable=False, quote=False)
    fromUser: Mapped["User"] = relationship("User", foreign_keys=[fromUserId])

    toUserId: Mapped[UUID] = mapped_column("toUserId", ForeignKey("users.id"), nullable=False, quote=False)
    toUser: Mapped["User"] = relationship("User", foreign_keys=[toUserId])

    amount: Mapped[int] = mapped_column("amount", Integer, nullable=False, quote=False)
    date: Mapped[date] = mapped_column("date", Date, default=datetime.utcnow().date(), server_default=text("(current_date at time zone 'utc')"), nullable=False, quote=False)
