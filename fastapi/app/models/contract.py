import os
from datetime import datetime, date
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base

from typing import Self, List

from .accounts import Account
from .contractPhoto import ContractPhoto
from .transactions import TransactionHeader
from ..services.accounts_helpers import AccountTypes


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        CheckConstraint("startdate <= enddate"),
        CheckConstraint("isdraft = true OR clientid NOT NULL"),
        CheckConstraint("isdraft = true OR bikeid NOT NULL"),
        CheckConstraint("isdraft = true OR workinguserid NOT NULL"),
        CheckConstraint("isdraft = true OR checkinguserid NOT NULL"),
        CheckConstraint("isdraft = true OR startdate NOT NULL"),
        CheckConstraint("isdraft = true OR enddate NOT NULL"),
        CheckConstraint("isdraft = true OR conditionofbike NOT NULL"),
        CheckConstraint("isdraft = true OR contracttype NOT NULL")
    )

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientid", ForeignKey("clients.id"), nullable=True, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")

    bikeId: Mapped[UUID] = mapped_column("bikeid", ForeignKey("bikes.id"), nullable=True, quote=False)
    bike: Mapped["Bike"] = relationship("Bike", back_populates="contracts")

    workingUserId: Mapped[UUID] = mapped_column("workinguserid", ForeignKey("users.id"), nullable=True, quote=False)
    workingUser: Mapped["User"] = relationship("User", foreign_keys=[workingUserId], back_populates="workedContracts")

    checkingUserId: Mapped[UUID] = mapped_column("checkinguserid", ForeignKey("users.id"), nullable=True, quote=False)
    checkingUser: Mapped["User"] = relationship("User", foreign_keys=[checkingUserId], back_populates="checkedContracts")

    returnAcceptingUserId: Mapped[UUID] = mapped_column("returnacceptinguserid", ForeignKey("users.id"), nullable=True, server_default=text("NULL"), default=None, quote=False)
    returnAcceptingUser: Mapped["User"] = relationship("User", foreign_keys=[returnAcceptingUserId], back_populates="returnedContracts")

    startDate: Mapped[date] = mapped_column("startdate", Date, nullable=True, index=True, quote=False)
    endDate: Mapped[date] = mapped_column("enddate", Date, nullable=True, index=True, quote=False)

    returnedDate: Mapped[date] = mapped_column("returneddate", Date, nullable=True, quote=False, server_default=text("NULL"), default=None)

    conditionOfBike: Mapped[str] = mapped_column("conditionofbike", String(20), nullable=True, quote=False)
    contractType: Mapped[str] = mapped_column("contracttype", String(20), nullable=True, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)

    detailsSent: Mapped[bool] = mapped_column("detailssent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    expiryReminderSent: Mapped[bool] = mapped_column("expiryremindersent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    liabilityDormantSent: Mapped[bool] = mapped_column("liabilitydormantsent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    returnDetailsSent: Mapped[bool] = mapped_column("returndetailssent", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    isDraft: Mapped[bool] = mapped_column("isdraft", Boolean, nullable=False, default=True, server_default=text("TRUE"), quote=False)

    crimeReports: Mapped[List["CrimeReport"]] = relationship("CrimeReport", back_populates="contract")

    depositTransactionHeaders: Mapped[List["TransactionHeader"]] = relationship("TransactionHeader", foreign_keys=[TransactionHeader.contractId], back_populates="contract")
    photos: Mapped[List["ContractPhoto"]] = relationship("ContractPhoto", foreign_keys=[ContractPhoto.contractId], back_populates="contract")


    @property
    def liability_collected_transaction_header(self) -> TransactionHeader | None:
        for th in self.depositTransactionHeaders:
            if th.event == "deposit_collected":
                return th
        return None
    
    @property
    def liability_collected_account(self) -> Account | None:
        th = self.liability_collected_transaction_header
        if th is not None:
            for tl in th.transactionLines:
                if tl.account.type == AccountTypes.ASSET:
                    return tl.account
        return None

    @property
    def liability_collected(self) -> int:
        th = self.liability_collected_transaction_header
        if th is not None:
            for tl in th.transactionLines:
                if tl.account.type == AccountTypes.LIABILITY:
                    return abs(tl.amount)
                    
        return 0
    
    @property
    def liability_collected_string(self) -> str:
        return f"{(self.liability_collected / 100):.2f}"
    
    @property
    def deposit_returned_transaction_header(self) -> TransactionHeader | None:
        for th in self.depositTransactionHeaders:
            if th.event == "deposit_settled":
                return th
        return None
    
    @property
    def deposit_returned_account(self) -> Account | None:
        th = self.deposit_returned_transaction_header
        if th is not None:
            for tl in th.transactionLines:
                if tl.account.type == AccountTypes.ASSET:
                    return tl.account
        return None
    
    @property
    def deposit_amount_returned(self) -> int:
        th = self.deposit_returned_transaction_header
        if th is not None:
            for tl in th.transactionLines:
                if tl.account.type == AccountTypes.ASSET:
                    return abs(tl.amount)
        return None
    
    @property
    def deposit_amount_returned_string(self) -> str:
        return f"{(self.deposit_amount_returned / 100):.2f}" if self.deposit_amount_returned is not None else ""

    def __eq__dict(self, other: dict):
        return all([
            # TODO: deposit information needs to use new model
            str(self.id) == str(other.get("id")),
            str(self.clientId) == str(other.get("clientId")),
            str(self.bikeId) == str(other.get("bikeId")),
            str(self.workingUserId) == str(other.get("workingUserId")),
            str(self.checkingUserId) == str(other.get("checkingUserId")),
            str(self.returnAcceptingUserId) == str(other.get("returnAcceptingUserId")),
            str(self.startDate) == str(other.get("startDate")),
            str(self.endDate) == str(other.get("endDate")),
            str(self.returnedDate) == str(other.get("returnedDate")),
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
            # TODO: deposit information needs to use new model
            str(self.id) == str(other.id),
            str(self.clientId) == str(other.clientId),
            str(self.bikeId) == str(other.bikeId),
            str(self.workingUserId) == str(other.workingUserId),
            str(self.checkingUserId) == str(other.checkingUserId),
            str(self.returnAcceptingUserId) == str(other.returnAcceptingUserId),
            str(self.startDate) == str(other.startDate),
            str(self.endDate) == str(other.endDate),
            str(self.returnedDate) == str(other.returnedDate),
            str(self.conditionOfBike) == str(other.conditionOfBike),
            str(self.contractType) == str(other.contractType),
            str(self.notes) == str(other.notes),
            str(self.detailsSent) == str(other.detailsSent),
            str(self.expiryReminderSent) == str(other.expiryReminderSent),
            str(self.returnDetailsSent) == str(other.returnDetailsSent),
        ])

    def send_creation_email(self):
        email_html_content = services.email_helpers.render_template(template_name="contract_created", client=self.client, contract=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Bike Rental Contract",
            content=email_html_content
        )

    def send_expiry_reminder_email(self) -> bool:
        email_html_content = services.email_helpers.render_template(template_name="contract_expiry_reminder", client=self.client, contract=self)
        return services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Bike Rental Expiry Reminder",
            content=email_html_content
        )

    def send_return_email(self):
        email_html_content = services.email_helpers.render_template(template_name="contract_returned", client=self.client, contract=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Bike Rental Has Ended",
            content=email_html_content
        )
        
    def send_contract_grace_period_ended_email(self) -> bool:
        email_html_content = services.email_helpers.render_template(template_name="contract_grace_period_ended", client=self.client, contract=self)
        return services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Bike Rental Has Expired!",
            content=email_html_content
        )
        
    def send_deposit_forfeited_email(self) -> bool:
        email_html_content = services.email_helpers.render_template(template_name="contract_deposit_forfeited", client=self.client, contract=self)
        return services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Bike Rental Deposit Has Been Forfeited",
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
            # TODO: deposit information needs to use new model
            "Deposit Amount Collected": self.liability_collected_string,
            "Deposit Collected By": self.liability_collected_account.name if self.liability_collected_account is not None else None,
            "Returned Date": self.returnedDate,
            "Returned Date-day": "{:02d}".format(self.returnedDate.day) if self.returnedDate is not None else None,
            "Returned Date-month": "{:02d}".format(self.returnedDate.month) if self.returnedDate is not None else None,
            "Returned Date-year": "{:04d}".format(self.returnedDate.year) if self.returnedDate is not None else None,
            "Return Received By": self.returnAcceptingUser.username if self.returnAcceptingUser is not None else None,
            "Deposit Amount Returned": self.deposit_amount_returned_string,
            "Deposit Returned By": self.deposit_returned_account.name if self.deposit_returned_account is not None else None,
            "Draft": self.isDraft
        }


class PaperContract(Base):
    __tablename__ = "papercontracts"

    id: Mapped[str] = mapped_column("id", String(24), primary_key=True, nullable=False, index=True, quote=False)

    contractId: Mapped[UUID] = mapped_column("contractid", ForeignKey("contracts.id"), nullable=False, quote=False)
    contract: Mapped[Contract] = relationship("Contract")

