import os
from datetime import datetime
from random import random
from typing import List
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base

CLIENT_LOGIN_CODE_EXPIRE_MINUTES = int(os.environ['CLIENT_LOGIN_CODE_EXPIRE_MINUTES'])
CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES = int(os.environ['CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES'])


def generate_6_digit_code():
    return "{:06d}".format(int(random() * 1000000))


def generate_6_digit_code_sql():
    return text("TO_CHAR(FLOOR(RANDOM()*1000000), 'fm000000')")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)
    firstName: Mapped[str] = mapped_column("firstName", String(40), nullable=False, index=True, quote=False)
    lastName: Mapped[str] = mapped_column("lastName", String(40), nullable=False, index=True, quote=False)
    emailAddress: Mapped[str] = mapped_column("emailAddress", String(255), nullable=False,
                                              quote=False)  # , unique=True)
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="client")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="client")

    preBecycleSurveyCompleted: Mapped[bool] = mapped_column("preBecycleSurveyCompleted", Boolean, default=False, server_default=text("FALSE"),
                                                nullable=False,
                                                quote=False)
    periBecycleSurveyCompleted: Mapped[bool] = mapped_column("periBecycleSurveyCompleted", Boolean, default=False,
                                                            server_default=text("FALSE"),
                                                            nullable=False,
                                                            quote=False)
    postBecycleSurveyCompleted: Mapped[bool] = mapped_column("postBecycleSurveyCompleted", Boolean, default=False,
                                                             server_default=text("FALSE"),
                                                             nullable=False,
                                                             quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.firstName) == str(other.get("firstName")),
            str(self.lastName) == str(other.get("lastName")),
            str(self.emailAddress) == str(other.get("emailAddress"))
        ])


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

    verificationCode: Mapped[str] = mapped_column("verificationCode", String(6), nullable=False,
                                                       default=lambda: generate_6_digit_code(),
                                                       server_default=generate_6_digit_code_sql(), quote=False)
    expirationDateTime: Mapped[DateTime] = mapped_column("expirationDateTime", DateTime,
                                                         default=lambda: datetime.utcnow() + relativedelta(
                                                             minutes=CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES),
                                                         server_default=text(
                                                             "(current_timestamp at time zone 'utc' + make_interval(mins => {:d}))".format(
                                                                 CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES)), nullable=False,
                                                         quote=False)

    def send_email_verification_link(self):
        email_html_content = services.email_helpers.build_email_verification_html(
            client_temp_id=self.id, verification_code=self.verificationCode)
        services.email_helpers.send_email(
            destination=self.emailAddress,
            subject="Verify your email address",
            content=email_html_content)


class ClientLogin(Base):
    # this is where temporary login codes for clients get stored
    __tablename__ = "clientlogins"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client")

    code: Mapped[DateTime] = mapped_column("code", String(6), nullable=False,
                                           default=lambda: generate_6_digit_code(),
                                           server_default=generate_6_digit_code_sql(), quote=False)
    expirationDateTime: Mapped[DateTime] = mapped_column("expirationDateTime", DateTime,
                                                         default=lambda: datetime.utcnow() + relativedelta(
                                                             minutes=CLIENT_LOGIN_CODE_EXPIRE_MINUTES),
                                                         server_default=text(
                                                             "(current_timestamp at time zone 'utc' + make_interval(mins => {:d}))".format(
                                                                 CLIENT_LOGIN_CODE_EXPIRE_MINUTES)),
                                                         nullable=False, quote=False)

    def send_login_code(self):
        email_html_content = services.email_helpers.build_client_login_code_html(login_code=self.code)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Log-in code",
            content=email_html_content)
