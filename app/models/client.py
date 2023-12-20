from sqlalchemy import String, UUID, text
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from typing import List


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    firstName: Mapped[str] = mapped_column("firstName", String(40), nullable=False, index=True, quote=False)
    lastName: Mapped[str] = mapped_column("lastName", String(40), nullable=False, index=True, quote=False)
    emailAddress: Mapped[str] = mapped_column("emailAddress", String(255), nullable=False, quote=False)
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="client")
