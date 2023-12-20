from sqlalchemy import String, UUID, Boolean, text
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from typing import List
from .contract import Contract


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    username: Mapped[str] = mapped_column("username", String(40), nullable=False, index=True, quote=False, unique=True)
    password: Mapped[str] = mapped_column("password", String(60), nullable=False, index=True, quote=False)
    pin: Mapped[str] = mapped_column("pin", String(60), nullable=True, quote=False)
    admin: Mapped[bool] = mapped_column("admin", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    depositBearer: Mapped[bool] = mapped_column("depositBearer", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    rentalChecker: Mapped[bool] = mapped_column("rentalChecker", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    appointmentManager: Mapped[bool] = mapped_column("appointmentManager", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    treasurer: Mapped[bool] = mapped_column("treasurer", Boolean, default=False, nullable=False, server_default=text("FALSE"), quote=False)
    softDeleted: Mapped[bool] = mapped_column("softDeleted", Boolean, default=False, nullable=False, server_default=text("FALSE"), quote=False)

    workedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.workingUserId], back_populates="workingUser")
    checkedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.checkingUserId], back_populates="checkingUser")
    depositCollectedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.depositCollectingUserId], back_populates="depositCollectingUser")
    returnedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.returnAcceptingUserId], back_populates="returnAcceptingUser")
    depositReturnedContracts: Mapped[List["Contract"]] = relationship("Contract", foreign_keys=[Contract.depositReturningUserId], back_populates="depositReturningUser")
