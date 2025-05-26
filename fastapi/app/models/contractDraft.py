import os
from datetime import datetime, date
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base

from typing import Self

CONTRACT_EXPIRE_MONTHS = int(os.environ['CONTRACT_EXPIRE_MONTHS'])


class ContractDraft(Base):
    __tablename__ = "contractdrafts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientid", ForeignKey("clients.id"), nullable=True, quote=False)
    client: Mapped["Client"] = relationship("Client", foreign_keys=[clientId])

    bikeId: Mapped[UUID] = mapped_column("bikeid", ForeignKey("bikes.id"), nullable=True, quote=False)
    bike: Mapped["Bike"] = relationship("Bike", foreign_keys=[bikeId])

    workingUserId: Mapped[UUID] = mapped_column("workinguserid", ForeignKey("users.id"), nullable=True, quote=False)
    workingUser: Mapped["User"] = relationship("User", foreign_keys=[workingUserId])

    checkingUserId: Mapped[UUID] = mapped_column("checkinguserid", ForeignKey("users.id"), nullable=True, quote=False)
    checkingUser: Mapped["User"] = relationship("User", foreign_keys=[checkingUserId])

    depositCollectingUserId: Mapped[UUID] = mapped_column("depositcollectinguserid", ForeignKey("users.id"), nullable=True, quote=False)
    depositCollectingUser: Mapped["User"] = relationship("User", foreign_keys=[depositCollectingUserId])


    startDate: Mapped[date] = mapped_column("startdate", Date, default=datetime.utcnow().date(), server_default=text("(current_date at time zone 'utc')"), nullable=False, index=True, quote=False)
    endDate: Mapped[date] = mapped_column("enddate", Date, default=datetime.utcnow().date() + relativedelta(months=CONTRACT_EXPIRE_MONTHS), server_default=text("(current_date at time zone 'utc' + make_interval(months => {:d}))".format(CONTRACT_EXPIRE_MONTHS)), nullable=False, index=True, quote=False)


    depositAmountCollected: Mapped[int] = mapped_column("depositamountcollected", Integer, nullable=True, quote=False)

    conditionOfBike: Mapped[str] = mapped_column("conditionofbike", String(20), nullable=True, quote=False)
    contractType: Mapped[str] = mapped_column("contracttype", String(20), nullable=True, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    def __eq__dict(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.clientId) == str(other.get("clientId")),
            str(self.bikeId) == str(other.get("bikeId")),
            str(self.workingUserId) == str(other.get("workingUserId")),
            str(self.checkingUserId) == str(other.get("checkingUserId")),
            str(self.depositCollectingUserId) == str(other.get("depositCollectingUserId")),
            # str(self.returnAcceptingUserId) == str(other.get("returnAcceptingUserId")),
            # str(self.depositReturningUserId) == str(other.get("depositReturningUserId")),
            str(self.startDate) == str(other.get("startDate")),
            str(self.endDate) == str(other.get("endDate")),
            # str(self.returnedDate) == str(other.get("returnedDate")),
            str(self.depositAmountCollected) == str(other.get("depositAmountCollected")),
            # str(self.depositAmountReturned) == str(other.get("depositAmountReturned")),
            str(self.conditionOfBike) == str(other.get("conditionOfBike")),
            str(self.contractType) == str(other.get("contractType")),
            str(self.notes) == str(other.get("notes")),
            # str(self.detailsSent) == str(other.get("detailsSent")),
            # str(self.expiryReminderSent) == str(other.get("expiryReminderSent")),
            # str(self.returnDetailsSent) == str(other.get("returnDetailsSent")),
        ])

    def __eq__(self, other):
        if type(other) is dict:
            return self.__eq__dict(other)
        return all([
            str(self.id) == str(other.id),
            str(self.clientId) == str(other.clientId),
            str(self.bikeId) == str(other.bikeId),
            str(self.workingUserId) == str(other.workingUserId),
            str(self.checkingUserId) == str(other.checkingUserId),
            str(self.depositCollectingUserId) == str(other.depositCollectingUserId),
            # str(self.returnAcceptingUserId) == str(other.returnAcceptingUserId),
            # str(self.depositReturningUserId) == str(other.depositReturningUserId),
            str(self.startDate) == str(other.startDate),
            str(self.endDate) == str(other.endDate),
            # str(self.returnedDate) == str(other.returnedDate),
            str(self.depositAmountCollected) == str(other.depositAmountCollected),
            # str(self.depositAmountReturned) == str(other.depositAmountReturned),
            str(self.conditionOfBike) == str(other.conditionOfBike),
            str(self.contractType) == str(other.contractType),
            str(self.notes) == str(other.notes),
            # str(self.detailsSent) == str(other.detailsSent),
            # str(self.expiryReminderSent) == str(other.expiryReminderSent),
            # str(self.returnDetailsSent) == str(other.returnDetailsSent),
        ])