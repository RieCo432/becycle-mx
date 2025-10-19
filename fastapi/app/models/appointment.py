from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, text, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.services as services
from app.database.db import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    clientId: Mapped[UUID] = mapped_column("clientid", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="appointments")

    typeId: Mapped[str] = mapped_column("typeid", ForeignKey("appointmenttypes.id"), nullable=False, quote=False)
    type: Mapped["AppointmentType"] = relationship("AppointmentType")

    startDateTime: Mapped[datetime] = mapped_column("startdatetime", DateTime, nullable=False, quote=False, index=True)
    endDateTime: Mapped[datetime] = mapped_column("enddatetime", DateTime, nullable=False, quote=False)

    notes: Mapped[str] = mapped_column("notes", Text, nullable=True, quote=False)
    confirmed: Mapped[bool] = mapped_column("confirmed", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    cancelled: Mapped[bool] = mapped_column("cancelled", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)

    reminderSent: Mapped[bool] = mapped_column("remindersent", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)

    cancellationReason: Mapped[str] = mapped_column("cancellationreason", Text, nullable=True, quote=False)


    def __eq_dict__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.clientId) == str(other.get("clientId")),
            str(self.typeId) == str(other.get("typeId")),
            self.startDateTime == datetime.strptime(other.get("startDateTime"), "%Y-%m-%dT%H:%M:%S"),
            self.endDateTime == datetime.strptime(other.get("endDateTime"), "%Y-%m-%dT%H:%M:%S"),
            str(self.notes) == str(other.get("notes")),
            str(self.confirmed) == str(other.get("confirmed")),
            str(self.cancelled) == str(other.get("cancelled")),
            str(self.reminderSent) == str(other.get("reminderSent")),
        ])

    def __eq__(self, other):
        if type(other) is dict:
            return self.__eq_dict__(other)
        else:
            return all([
                self.id == other.id,
                self.clientId == other.clientId,
                self.typeId == other.typeId,
                self.startDateTime == other.startDateTime,
                self.endDateTime == other.endDateTime,
                self.notes == other.notes,
                self.confirmed == other.confirmed,
                self.cancelled == other.cancelled,
                self.reminderSent == other.reminderSent
            ])

    def send_request_received_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_request_received", client=self.client, appointment=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Request Has Been Received",
            content=email_html_content
        )

    def send_confirmation_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_confirmation", client=self.client, appointment=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Has Been Confirmed",
            content=email_html_content
        )

    def send_request_denied_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_request_denied", client=self.client, appointment=self)
        services.email_helpers.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Request Has Been Denied",
            content=email_html_content
        )

    def send_cancellation_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_cancelled_by_us", client=self.client, appointment=self)
        services.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Has Been Cancelled",
            content=email_html_content
        )

    def send_client_cancellation_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_cancelled_by_client", client=self.client, appointment=self)
        services.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Has Been Cancelled",
            content=email_html_content
        )

    def send_reminder_email(self):
        email_html_content = services.email_helpers.render_template(template_name="appointment_reminder", client=self.client, appointment=self)
        services.send_email(
            destination=self.client.emailAddress,
            subject="Your Appointment Reminder",
            content=email_html_content
        )
