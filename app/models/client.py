from sqlalchemy import String, UUID
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from app.database.db import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column(UUID, name="id", primary_key=True, nullable=False, default=uuid4, index=True, quote=False)
    firstName: Mapped[str] = mapped_column(String(40), name="firstName", nullable=False, index=True, quote=False)
    lastName: Mapped[str] = mapped_column(String(40), name="lastName", nullable=False, index=True, quote=False)
    emailAddress: Mapped[str] = mapped_column(String(255), name="emailAddress", nullable=False, quote=False)

