from datetime import datetime
from sqlalchemy import UUID, text, ForeignKey, Text, Boolean, DateTime
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class Contract(Base):
    __tablename__ = "appointments"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="appointments")

    appointmentTypeId: Mapped[str] = mapped_column("appointmentTypeId", ForeignKey("appointmenttypes.id"), nullable=False, quote=False)
    appointmentType: Mapped["AppointmentType"] = relationship("AppointmentType")

    startDateTime: Mapped[datetime] = mapped_column("startDateTime", DateTime, nullable=False, quote=False)
    endDateTime: Mapped[datetime] = mapped_column("endDateTime", DateTime, nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)
    confirmed: Mapped[bool] = mapped_column("confirmed", Boolean, nullable=False, quote=False)
    cancelled: Mapped[bool] = mapped_column("cancelled", Boolean, nullable=False, quote=False)

    reminderSent: Mapped[bool] = mapped_column("reminderSent", Boolean, nullable=False, quote=False)
