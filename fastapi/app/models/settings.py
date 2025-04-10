from datetime import time, date
from uuid import uuid4

from sqlalchemy import String, text, Boolean, Text, Integer, ARRAY, Time, Date, PrimaryKeyConstraint, UUID, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class AppointmentGeneralSettings(Base):
    __tablename__ = "appointmentgeneralsettings"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, nullable=False, default=1, server_default=text("1"), index=True, quote=False)
    openingDays: Mapped[list[int]] = mapped_column("openingdays", ARRAY(Integer), nullable=False, quote=False)
    minBookAhead: Mapped[int] = mapped_column("minbookahead", Integer, nullable=False, quote=False)
    maxBookAhead: Mapped[int] = mapped_column("maxbookahead", Integer, nullable=False, quote=False)
    slotDuration: Mapped[int] = mapped_column("slotduration", Integer, nullable=False, quote=False)
    gradualAvailability: Mapped[bool] = mapped_column("gradualavailability", Boolean, nullable=False, quote=False, default=False, server_default=text("FALSE"))


class AppointmentConcurrencyLimit(Base):
    __tablename__ = "appointmentconcurrencylimits"

    weekDay: Mapped[int] = mapped_column("weekday", Integer, primary_key=True, nullable=False, index=True, quote=False)
    afterTime: Mapped[time] = mapped_column("aftertime", Time, primary_key=True, nullable=False, index=True, quote=False)
    maxConcurrent: Mapped[int] = mapped_column("maxconcurrent", Integer, nullable=False, quote=False)

    __table_args__ = (
        PrimaryKeyConstraint(weekDay, afterTime),
        {}
    )

    def __eq__(self, other: dict):
        return all([
            str(self.weekDay) == str(other["weekday"]),
            str(self.afterTime) == str(other.get("afterTime")),
            str(self.maxConcurrent) == str(other.get("maxConcurrent"))
        ])


class AppointmentType(Base):
    __tablename__ = "appointmenttypes"

    id: Mapped[str] = mapped_column("id", String(5), primary_key=True, nullable=False, index=True, quote=False)
    active: Mapped[bool] = mapped_column("active", Boolean, nullable=False, default=True, server_default=text("TRUE"), quote=False)
    title: Mapped[str] = mapped_column("title", String(40), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)
    duration: Mapped[int] = mapped_column("duration", Integer, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.active) == str(other.get("active")),
            str(self.title) == str(other.get("title")),
            str(self.description) == str(other.get("description")),
            str(self.duration) == str(other.get("duration")),
        ])


class ClosedDay(Base):
    __tablename__ = "closeddays"

    date: Mapped[date] = mapped_column("date", Date, primary_key=True, nullable=False, index=True, quote=False)
    note: Mapped[str] = mapped_column("note", Text, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            self.date.strftime("%Y-%m-%d") == str(other.get("date")),
            str(self.note) == str(other.get("note"))
        ])


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, nullable=False, default=1, server_default=text("1"), index=True, quote=False)
    number: Mapped[str] = mapped_column("number", Text, nullable=False, quote=False)
    street: Mapped[str] = mapped_column("street", Text, nullable=False, quote=False)
    postcode: Mapped[str] = mapped_column("postcode", Text, nullable=False, quote=False)
    city: Mapped[str] = mapped_column("city", Text, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.number) == str(other.get("number")),
            str(self.street) == str(other.get("street")),
            str(self.postcode) == str(other.get("postcode")),
            str(self.city) == str(other.get("city"))
        ])


class AboutUs(Base):
    __tablename__ = "aboutus"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, nullable=False, default=1, server_default=text("1"), index=True, quote=False)
    html: Mapped[str] = mapped_column("html", Text, nullable=True, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.html) == str(other.get("number")),
        ])


class Faq(Base):
    __tablename__ = "faqs"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)
    question: Mapped[str] = mapped_column("question", String(256), nullable=False, quote=False)
    answer: Mapped[str] = mapped_column("answer", Text, nullable=False, quote=False)
    active: Mapped[bool] = mapped_column("active", Boolean, nullable=False, default=True, server_default=text("TRUE"),
                                         quote=False)
    orderIndex: Mapped[int] = mapped_column("orderindex", Integer, Identity(start=1, cycle=True), unique=True, index=True, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.active) == str(other.get("active")),
            str(self.question) == str(other.get("question")),
            str(self.answer) == str(other.get("answer")),
            str(self.orderIndex) == str(other.get("orderIndex")),
        ])


class ContractType(Base):
    __tablename__ = "contracttypes"

    id: Mapped[str] = mapped_column("id", String(20), nullable=False, quote=False, primary_key=True)

    def __eq__(self, other: dict):
        return str(self.id) == str(other.get("id"))


class ExpenseType(Base):
    __tablename__ = "expensetypes"

    id: Mapped[str] = mapped_column("id", String(20), nullable=False, quote=False, primary_key=True)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            self.id == other.get("id"),
            self.description == other.get("description")
        ])
