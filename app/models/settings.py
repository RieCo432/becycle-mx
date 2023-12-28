from sqlalchemy import String, text, Boolean, Text, Integer, ARRAY, Time
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from app.database.db import Base
from datetime import time


class AppointmentGeneral(Base):
    __tablename__ = "appointmentgeneral"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, nullable=False, default=1, server_default=text("1"), index=True, quote=False)
    openingDays: Mapped[list[int]] = mapped_column("openingDays", ARRAY(Integer), nullable=False, quote=False)
    minBookAhead: Mapped[int] = mapped_column("minBookAhead", Integer, nullable=False, quote=False)
    maxBookAhead: Mapped[int] = mapped_column("maxBookAhead", Integer, nullable=False, quote=False)
    slotDuration: Mapped[int] = mapped_column("slotDuration", Integer, nullable=False, quote=False)


class AppointmentConcurrency(Base):
    __tablename__ = "appointmentconcurrency"

    afterTime: Mapped[time] = mapped_column("afterTime", Time, primary_key=True, nullable=False, index=True, quote=False)
    maxConcurrent: Mapped[int] = mapped_column("maxConcurrent", Integer, nullable=False, quote=False)


class AppointmentType(Base):
    __tablename__ = "appointmenttypes"

    id: Mapped[str] = mapped_column("id", String(5), primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    active: Mapped[bool] = mapped_column("active", Boolean, nullable=False, default=True, server_default=text("TRUE"), quote=False)
    title: Mapped[str] = mapped_column("title", String(40), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)
    duration: Mapped[int] = mapped_column("duration", Integer, nullable=False, quote=False)
