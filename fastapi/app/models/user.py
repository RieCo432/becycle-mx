from datetime import datetime
from typing import List
from uuid import uuid4

from pypdf.constants import UserAccessPermissions
from sqlalchemy import String, UUID, Boolean, text, Text, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from .contract import Contract
from .depositExchange import DepositExchange
from .expense import Expense
from .userPermission import UserPermission


class UserPhoto(Base):
    __tablename__ = "userphotos"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    content: Mapped[bytes] = mapped_column("content", LargeBinary, nullable=False, quote=False)


class UserPresentationCard(Base):
    __tablename__ = "userpresentationcards"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    userId: Mapped[UUID] = mapped_column("userid", ForeignKey("users.id"), nullable=False, quote=False)
    user: Mapped["User"] = relationship("User", foreign_keys=[userId], back_populates="presentationCard")

    name: Mapped[str] = mapped_column("name", String(40), nullable=False, index=True, quote=False, unique=True)
    bio: Mapped[str] = mapped_column("bio", Text, nullable=False, index=True, quote=False)

    photoFileId: Mapped[UUID] = mapped_column("photofileid", ForeignKey(UserPhoto.id), nullable=True,
                                                default=None, server_default=text("NULL"), quote=False)
    photoFile: Mapped["UserPhoto"] = relationship(UserPhoto, foreign_keys=[photoFileId])

    photoContentType: Mapped[str] = mapped_column("photocontenttype", Text, nullable=True, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.name) == str(other.get("name")),
            str(self.bio) == str(other.get("bio")),
            str(self.photoContentType) == str(other.get("photoContentType")),
        ])


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    username: Mapped[str] = mapped_column("username", String(40), nullable=False, index=True, quote=False, unique=True)
    password: Mapped[str] = mapped_column("password", String(60), nullable=False, index=True, quote=False)
    pin: Mapped[str] = mapped_column("pin", String(60), nullable=True, quote=False)
    admin: Mapped[bool] = mapped_column("admin", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    depositBearer: Mapped[bool] = mapped_column("depositbearer", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    rentalChecker: Mapped[bool] = mapped_column("rentalchecker", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    appointmentManager: Mapped[bool] = mapped_column("appointmentmanager", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    treasurer: Mapped[bool] = mapped_column("treasurer", Boolean, default=False, nullable=False, server_default=text("FALSE"), quote=False)
    softDeleted: Mapped[bool] = mapped_column("softdeleted", Boolean, default=False, nullable=False, server_default=text("FALSE"), quote=False)
    lastAuthenticated: Mapped[datetime] = mapped_column("lastauthenticated", DateTime, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), nullable=True, quote=False)

    workedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.workingUserId], back_populates="workingUser")
    checkedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.checkingUserId], back_populates="checkingUser")
    depositCollectedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.depositCollectingUserId], back_populates="depositCollectingUser")
    returnedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.returnAcceptingUserId], back_populates="returnAcceptingUser")
    depositReturnedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.depositReturningUserId], back_populates="depositReturningUser")

    depositExchangesReceived: Mapped[List[DepositExchange]] = relationship("DepositExchange", foreign_keys=[DepositExchange.toUserId], back_populates="toUser")
    depositExchangesGiven: Mapped[List[DepositExchange]] = relationship("DepositExchange", foreign_keys=[DepositExchange.fromUserId], back_populates="fromUser")

    expenses: Mapped[List["Expense"]] = relationship("Expense", foreign_keys=[Expense.expenseUserId], back_populates="expenseUser")
    transfers: Mapped[List["Expense"]] = relationship("Expense", foreign_keys=[Expense.treasurerUserId],
                                                     back_populates="treasurerUser")

    presentationCard: Mapped["UserPresentationCard"] = relationship("UserPresentationCard", foreign_keys=[UserPresentationCard.userId],
                                                             back_populates="user")

    userPermissions: Mapped[List["UserPermission"]] = relationship("UserPermission", foreign_keys=[UserPermission.userId],
                                                             back_populates="user")

    def __eq_dict__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.username) == str(other.get("username")),
            str(self.admin) == str(other.get("admin")),
            str(self.depositBearer) == str(other.get("depositBearer")),
            str(self.rentalChecker) == str(other.get("rentalChecker")),
            str(self.appointmentManager) == str(other.get("appointmentManager")),
            str(self.treasurer) == str(other.get("treasurer")),
            str(self.softDeleted) == str(other.get("softDeleted")),
        ])

    def __eq__(self, other):
        if type(other) is dict:
            return self.__eq_dict__(other)
        else:
            return all([
                self.id == other.id,
                self.username == other.username,
                self.admin == other.admin,
                self.depositBearer == other.depositBearer,
                self.rentalChecker == other.rentalChecker,
                self.appointmentManager == other.appointmentManager,
                self.treasurer == other.treasurer,
                self.softDeleted == other.softDeleted
            ])

    def get_deposit_bearer_balance(self):
        contract_balance = sum([contract.depositAmountCollected for contract in self.depositCollectedContracts]) - sum(
            [contract.depositAmountReturned for contract in self.depositReturnedContracts])

        deposit_exchange_balance = sum(
            [deposit_exchange.amount for deposit_exchange in self.depositExchangesReceived]) - sum(
            [deposit_exchange.amount for deposit_exchange in self.depositExchangesGiven])

        return contract_balance + deposit_exchange_balance
