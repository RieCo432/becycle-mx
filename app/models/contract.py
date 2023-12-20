from sqlalchemy import String, UUID, text, ForeignKey
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base

class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    clientId: Mapped[UUID] = mapped_column("clientId", ForeignKey("clients.id"), nullable=False, quote=False)
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")

    # bike
    # workingUser
    # checkingUser
    # returnDoneByUser
    # depositCollectedByUser
    # depositReturnedByUser
    #
    # startDate
    # endDate
    # returnedDate
    #
    # depositAmountCollected
    # depositAmountReturned
    #
    # condition
    # contractType
    # notes
    #
    # detailsSent
    # expiryReminderSent
