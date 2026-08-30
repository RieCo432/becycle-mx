from typing import List
from uuid import uuid4

from datetime import datetime, date
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Boolean, ARRAY, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    name: Mapped[str] = mapped_column("name", String(32), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)
    isActive: Mapped[bool] = mapped_column("isactive", Boolean, nullable=False, default=True, server_default=text("TRUE"),
                                         quote=False)
    isDefault: Mapped[bool] = mapped_column("isdefault", Boolean, nullable=False, default=False, server_default=text("FALSE"),
                                          quote=False)

    transactionLines: Mapped[List["TransactionLine"]] = relationship("TransactionLine", back_populates="fund")
