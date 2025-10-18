import os
from datetime import datetime, date
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base

from typing import Self, List

CONTRACT_EXPIRE_MONTHS = int(os.environ['CONTRACT_EXPIRE_MONTHS'])


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientid", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")

    bikeId: Mapped[UUID] = mapped_column("bikeid", ForeignKey("bikes.id"), nullable=False, quote=False)
    bike: Mapped["Bike"] = relationship("Bike", back_populates="contracts")

    workingUserId: Mapped[UUID] = mapped_column("workinguserid", ForeignKey("users.id"), nullable=False, quote=False)
    workingUser: Mapped["User"] = relationship("User", foreign_keys=[workingUserId], back_populates="workedContracts")

    checkingUserId: Mapped[UUID] = mapped_column("checkinguserid", ForeignKey("users.id"), nullable=False, quote=False)
    checkingUser: Mapped["User"] = relationship("User", foreign_keys=[checkingUserId], back_populates="checkedContracts")

    depositCollectingUserId: Mapped[UUID] = mapped_column("depositcollectinguserid", ForeignKey("users.id"), nullable=False, quote=False)
    depositCollectingUser: Mapped["User"] = relationship("User", foreign_keys=[depositCollectingUserId], back_populates="depositCollectedContracts")

    returnAcceptingUserId: Mapped[UUID] = mapped_column("returnacceptinguserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    returnAcceptingUser: Mapped["User"] = relationship("User", foreign_keys=[returnAcceptingUserId], back_populates="returnedContracts")

    depositReturningUserId: Mapped[UUID] = mapped_column("depositreturninguserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    depositReturningUser: Mapped["User"] = relationship("User", foreign_keys=[depositReturningUserId], back_populates="depositReturnedContracts")

    startDate: Mapped[date] = mapped_column("startdate", Date, default=datetime.utcnow().date(), server_default=text("(current_date at time zone 'utc')"), nullable=False, index=True, quote=False)
    endDate: Mapped[date] = mapped_column("enddate", Date, default=datetime.utcnow().date() + relativedelta(months=CONTRACT_EXPIRE_MONTHS), server_default=text("(current_date at time zone 'utc' + make_interval(months => {:d}))".format(CONTRACT_EXPIRE_MONTHS)), nullable=False, index=True, quote=False)

    returnedDate: Mapped[date] = mapped_column("returneddate", Date, nullable=True, quote=False, server_default=text("NULL"), default=None)

    depositAmountCollected: Mapped[int] = mapped_column("depositamountcollected", Integer, nullable=False, quote=False)
    depositAmountReturned: Mapped[int] = mapped_column("depositamountreturned", Integer, nullable=True, quote=False, server_default=text("NULL"), default=None)

    conditionOfBike: Mapped[str] = mapped_column("conditionofbike", String(20), nullable=False, quote=False)
    contractType: Mapped[str] = mapped_column("contracttype", String(20), nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    detailsSent: Mapped[bool] = mapped_column("detailssent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    expiryReminderSent: Mapped[bool] = mapped_column("expiryremindersent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    returnDetailsSent: Mapped[bool] = mapped_column("returndetailssent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)

    crimeReports: Mapped[List["CrimeReport"]] = relationship("CrimeReport", back_populates="contract")

    def __eq__dict(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.clientId) == str(other.get("clientId")),
            str(self.bikeId) == str(other.get("bikeId")),
            str(self.workingUserId) == str(other.get("workingUserId")),
            str(self.checkingUserId) == str(other.get("checkingUserId")),
            str(self.depositCollectingUserId) == str(other.get("depositCollectingUserId")),
            str(self.returnAcceptingUserId) == str(other.get("returnAcceptingUserId")),
            str(self.depositReturningUserId) == str(other.get("depositReturningUserId")),
            str(self.startDate) == str(other.get("startDate")),
            str(self.endDate) == str(other.get("endDate")),
            str(self.returnedDate) == str(other.get("returnedDate")),
            str(self.depositAmountCollected) == str(other.get("depositAmountCollected")),
            str(self.depositAmountReturned) == str(other.get("depositAmountReturned")),
            str(self.conditionOfBike) == str(other.get("conditionOfBike")),
            str(self.contractType) == str(other.get("contractType")),
            str(self.notes) == str(other.get("notes")),
            str(self.detailsSent) == str(other.get("detailsSent")),
            str(self.expiryReminderSent) == str(other.get("expiryReminderSent")),
            str(self.returnDetailsSent) == str(other.get("returnDetailsSent")),
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
            str(self.returnAcceptingUserId) == str(other.returnAcceptingUserId),
            str(self.depositReturningUserId) == str(other.depositReturningUserId),
            str(self.startDate) == str(other.startDate),
            str(self.endDate) == str(other.endDate),
            str(self.returnedDate) == str(other.returnedDate),
            str(self.depositAmountCollected) == str(other.depositAmountCollected),
            str(self.depositAmountReturned) == str(other.depositAmountReturned),
            str(self.conditionOfBike) == str(other.conditionOfBike),
            str(self.contractType) == str(other.contractType),
            str(self.notes) == str(other.notes),
            str(self.detailsSent) == str(other.detailsSent),
            str(self.expiryReminderSent) == str(other.expiryReminderSent),
            str(self.returnDetailsSent) == str(other.returnDetailsSent),
        ])

    def send_creation_email(self):
        email_html_content = services.email_helpers.render_template(template_name="contract_created", contract=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your lending agreement",
            content=email_html_content
        )

    def send_expiry_reminder_email(self):
        email_html_content = services.email_helpers.render_template(template_name="contract_expiry_reminder", contract=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="BECYCLE Contract Expiry Reminder",
            content=email_html_content
        )

    def send_return_email(self):
        email_html_content = services.email_helpers.render_template(template_name="contract_returned", contract=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="You have returned your bike",
            content=email_html_content
        )

    def to_raw_dict(self):
        return {
            "SHORT": self.client.lastName[:2].upper() if self.client is not None else 'XX',
            "Name": "{:s} {:s}".format(self.client.firstName, self.client.lastName) if self.client is not None else "UNKNOWN",
            "Email Address": self.client.emailAddress if self.client is not None else "UNKNOWN",
            "Start Date": self.startDate,
            "Start Date-day": "{:02d}".format(self.startDate.day),
            "Start Date-month": "{:02d}".format(self.startDate.month),
            "Start Date-year": "{:04d}".format(self.startDate.year),
            "End Date": self.endDate,
            "End Date-day": "{:02d}".format(self.endDate.day),
            "End Date-month": "{:02d}".format(self.endDate.month),
            "End Date-year": "{:04d}".format(self.endDate.year),
            "Make": self.bike.make if self.bike is not None else "UNKNOWN",
            "Model": self.bike.model if self.bike is not None else "UNKNOWN",
            "Colour": self.bike.colour if self.bike is not None else "UNKNOWN",
            "Decals": self.bike.decals if self.bike is not None else "UNKNOWN",
            "Serial Number": self.bike.serialNumber if self.bike is not None else "UNKNOWN",
            "Condition": self.conditionOfBike,
            "Notes": self.notes,
            "Contract Type": self.contractType,
            "Working Volunteer": self.workingUser.username if self.workingUser is not None else "UNKNOWN",
            "Checking Volunteer": self.checkingUser.username if self.checkingUser is not None else "UNKNOWN",
            "Deposit Amount Collected": self.depositAmountCollected,
            "Deposit Collected By": self.depositCollectingUser.username if self.depositCollectingUser is not None else "UNKNOWN",
            "Returned Date": self.returnedDate,
            "Returned Date-day": "{:02d}".format(self.returnedDate.day) if self.returnedDate is not None else None,
            "Returned Date-month": "{:02d}".format(self.returnedDate.month) if self.returnedDate is not None else None,
            "Returned Date-year": "{:04d}".format(self.returnedDate.year) if self.returnedDate is not None else None,
            "Return Received By": self.returnAcceptingUser.username if self.returnAcceptingUser is not None else None,
            "Deposit Amount Returned": self.depositAmountReturned,
            "Deposit Returned By": self.depositReturningUser.username if self.depositReturningUser is not None else None
        }


class PaperContract(Base):
    __tablename__ = "papercontracts"

    id: Mapped[str] = mapped_column("id", String(24), primary_key=True, nullable=False, index=True, quote=False)

    contractId: Mapped[UUID] = mapped_column("contractid", ForeignKey("contracts.id"), nullable=False, quote=False)
    contract: Mapped[Contract] = relationship("Contract")

