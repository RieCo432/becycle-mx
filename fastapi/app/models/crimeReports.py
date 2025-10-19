from typing import List
from uuid import uuid4

from datetime import datetime
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import services
from app.database.db import Base


class CrimeReport(Base):
    __tablename__ = "crimereports"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    crimeNumber: Mapped[str] = mapped_column("crimenumber", String(40), nullable=False, quote=False)
    contractId: Mapped[UUID] = mapped_column("contractid", ForeignKey("contracts.id"), nullable=False, quote=False)
    contract: Mapped["Contract"] = relationship("Contract", back_populates="crimeReports")
    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)
    closedOn: Mapped[datetime] = mapped_column("closedon", DateTime, nullable=True, quote=False)


    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.contractId) == str(other.get("contractId", None)),
            str(self.crimeNumber) == str(other.get("crimeNumber", None)),
            str(self.createdOn) == str(other.get("createdOn", None))
        ])

    def send_crime_report_added_email(self):
        email_html_content = services.email_helpers.render_template(template_name="crime_report_created", client=self.contract.client, crimeReport=self)
        services.email_helpers.send_email(
            destination=self.contract.client.emailAddress,
            subject="Your Bike Has Been Reported As Stolen",
            content=email_html_content)

    def send_crime_report_closed_email(self):
        email_html_content = services.email_helpers.render_template(template_name="crime_report_closed", client=self.contract.client, crimeReport=self)
        services.email_helpers.send_email(
            destination=self.contract.client.emailAddress,
            subject="Your Stolen Bike Report Has Been Closed",
            content=email_html_content
        )