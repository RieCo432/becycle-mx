from sqlalchemy import String, UUID, text, DateTime, ForeignKey
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from typing import List
from random import random
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    firstName: Mapped[str] = mapped_column("firstName", String(40), nullable=False, index=True, quote=False)
    lastName: Mapped[str] = mapped_column("lastName", String(40), nullable=False, index=True, quote=False)
    emailAddress: Mapped[str] = mapped_column("emailAddress", String(255), nullable=False, quote=False, unique=True)
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="client")


class ClientTemp(Base):
    # This table is to hold client information before email is verified.
    # ID and verificationCode need to be submitted to API via HTTP PUT before expiration datetime is reached.
    # This results in a promotion of the names and email address to a full client, and the client temp entry is deleted
    __tablename__ = "clientstemp"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)
    firstName: Mapped[str] = mapped_column("firstName", String(40), nullable=False, index=True, quote=False)
    lastName: Mapped[str] = mapped_column("lastName", String(40), nullable=False, index=True, quote=False)
    emailAddress: Mapped[str] = mapped_column("emailAddress", String(255), nullable=False, quote=False, unique=True)

    verificationCode: Mapped[DateTime] = mapped_column("verificationCode", String(6), nullable=False, default="{:06d}".format(int(random()*1000000)), server_default=text("TO_CHAR(FLOOR(RANDOM()*1000000), 'fm000000')"), quote=False)
    expirationDateTime: Mapped[DateTime] = mapped_column("expirationDateTime", DateTime, default=datetime.utcnow() + relativedelta(hours=24), server_default=text("(current_timestamp at time zone 'utc' + make_interval(hours => 24))"), nullable=False, quote=False)


class ClientLogin(Base):
    # this is where temporary login codes for clients get stored
    __tablename__ = "clientlogins"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client")

    code: Mapped[DateTime] = mapped_column("code", String(6), nullable=False,
                                                       default="{:06d}".format(int(random() * 1000000)),
                                                       server_default=text(
                                                           "TO_CHAR(FLOOR(RANDOM()*1000000), 'fm000000')"), quote=False)
    expirationDateTime: Mapped[DateTime] = mapped_column("expirationDateTime", DateTime,
                                                         default=datetime.utcnow() + relativedelta(minutes=60),
                                                         server_default=text(
                                                             "(current_timestamp at time zone 'utc' + make_interval(minutes => 60))"),
                                                         nullable=False, quote=False)
