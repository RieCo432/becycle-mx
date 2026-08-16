from datetime import date
from uuid import uuid4

from sqlalchemy import String, UUID, text, ForeignKey, Date, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class ContractPhoto(Base):
    __tablename__ = "contractphotos"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    contractId: Mapped[UUID] = mapped_column("contractid", ForeignKey("contracts.id"), nullable=True, quote=False, index=True)
    contract: Mapped["Contract"] = relationship("Contract", foreign_keys=[contractId], back_populates="photos")

    contentType: Mapped[str] = mapped_column("contenttype", Text, nullable=False, quote=False)

    content: Mapped[bytes] = mapped_column("content", LargeBinary, nullable=False, quote=False)