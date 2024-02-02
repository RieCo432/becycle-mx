from datetime import datetime
from sqlalchemy import UUID, text, ForeignKey, Text, Boolean, DateTime
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
import app.services as services


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="appointments")

    typeId: Mapped[str] = mapped_column("typeId", ForeignKey("appointmenttypes.id"), nullable=False, quote=False)
    type: Mapped["AppointmentType"] = relationship("AppointmentType")

    startDateTime: Mapped[datetime] = mapped_column("startDateTime", DateTime, nullable=False, quote=False)
    endDateTime: Mapped[datetime] = mapped_column("endDateTime", DateTime, nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)
    confirmed: Mapped[bool] = mapped_column("confirmed", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    cancelled: Mapped[bool] = mapped_column("cancelled", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)

    reminderSent: Mapped[bool] = mapped_column("reminderSent", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)

    def send_request_received_email(self):
        email_html_content = services.email_helpers.build_appointment_request_received_email(self.type.title, self.startDateTime)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Appointment Request Received",
            content=email_html_content
        )

    def send_confirmation_email(self):
        email_html_content = services.email_helpers.build_appointment_confirmation_email(self.type.title, self.startDateTime)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Confirmation",
            content=email_html_content
        )

    def send_request_denied_email(self):
        email_html_content = services.email_helpers.build_appointment_request_denied_email(self.type.title, self.startDateTime)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Apoointment Request has been denied",
            content=email_html_content
        )

    def send_cancellation_email(self):
        email_html_content = services.email_helpers.build_appointment_cancellation_email(self.type.title, self.startDateTime)
        services.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment has been cancelled",
            content=email_html_content
        )
