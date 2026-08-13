from uuid import uuid4

from datetime import datetime
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class BugReport(Base):
    __tablename__ = "bugreports"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    reportedByUserId: Mapped[UUID] = mapped_column("reportedbyuserid", ForeignKey("users.id"), nullable=False, quote=False)
    reportedAt: Mapped[datetime] = mapped_column("reportedat", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)
    pageAddress: Mapped[str] = mapped_column("pageaddress", String(255), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", String(1024), nullable=False, quote=False)
    consoleHistory: Mapped[str] = mapped_column("consolehistory", Text, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id", None)),
            str(self.reportedByUserId) == str(other.get("reportedByUserId", None)),
            str(self.reportedAt) == str(other.get("reportedAt", None)),
            str(self.pageAddress) == str(other.get("pageAddress", None)),
            str(self.description) == str(other.get("description", None)),
            str(self.consoleHistory) == str(other.get("consoleHistory", None))
        ])