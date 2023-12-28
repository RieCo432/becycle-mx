from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import CONTRACT_EXPIRE_MONTHS
from app.database.db import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")

    bikeId: Mapped[UUID] = mapped_column("bikeId", ForeignKey("bikes.id"), nullable=False, quote=False)
    bike: Mapped["Bike"] = relationship("Bike", back_populates="contracts")

    workingUserId: Mapped[UUID] = mapped_column("workingUserId", ForeignKey("users.id"), nullable=False)
    workingUser: Mapped["User"] = relationship("User", foreign_keys=[workingUserId], back_populates="workedContracts")

    checkingUserId: Mapped[UUID] = mapped_column("checkingUserId", ForeignKey("users.id"), nullable=False)
    checkingUser: Mapped["User"] = relationship("User", foreign_keys=[checkingUserId], back_populates="checkedContracts")

    depositCollectingUserId: Mapped[UUID] = mapped_column("depositCollectingUserId", ForeignKey("users.id"), nullable=False)
    depositCollectingUser: Mapped["User"] = relationship("User", foreign_keys=[depositCollectingUserId], back_populates="depositCollectedContracts")

    returnAcceptingUserId: Mapped[UUID] = mapped_column("returnAcceptingUserId", ForeignKey("users.id"), nullable=True)
    returnAcceptingUser: Mapped["User"] = relationship("User", foreign_keys=[returnAcceptingUserId], back_populates="returnedContracts")

    depositReturningUserId: Mapped[UUID] = mapped_column("depositReturningUserId", ForeignKey("users.id"), nullable=True)
    depositReturningUser: Mapped["User"] = relationship("User", foreign_keys=[depositReturningUserId], back_populates="depositReturnedContracts")

    startDate: Mapped[date] = mapped_column("startDate", Date, default=datetime.utcnow().date(), server_default=text("(current_date at time zone 'utc')"), nullable=False, quote=False)
    endDate: Mapped[date] = mapped_column("endDate", Date, default=datetime.utcnow().date() + relativedelta(months=CONTRACT_EXPIRE_MONTHS), server_default=text("(current_date at time zone 'utc' + make_interval(months => {:d}))".format(CONTRACT_EXPIRE_MONTHS)), nullable=False, quote=False)

    returnedDate: Mapped[date] = mapped_column("returnedDate", Date, nullable=True, quote=False)

    depositAmountCollected: Mapped[int] = mapped_column("depositAmountCollected", Integer, nullable=False, quote=False)
    depositAmountReturned: Mapped[int] = mapped_column("depositAmountReturned", Integer, nullable=True, quote=False)

    conditionOfBike: Mapped[str] = mapped_column("conditionOfBike", String(20), nullable=False, quote=False)
    contractType: Mapped[str] = mapped_column("contractType", String(20), nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    detailsSent: Mapped[bool] = mapped_column("detailsSent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    expiryReminderSent: Mapped[bool] = mapped_column("expiryReminderSent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    returnDetailsSent: Mapped[bool] = mapped_column("returnDetailsSent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
