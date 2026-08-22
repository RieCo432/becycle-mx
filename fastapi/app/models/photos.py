from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, text, ForeignKey, String, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    userId: Mapped[UUID] = mapped_column("userid", ForeignKey("users.id"), nullable=False, quote=False, index=True)
    user: Mapped["User"] = relationship("User", foreign_keys=[userId], back_populates="photos")
    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, quote=False)

    contentType: Mapped[str] = mapped_column("contenttype", String(50), nullable=False, quote=False)

    thumbnail: Mapped[bytes] = mapped_column("thumbnail", LargeBinary, nullable=False, quote=False)
    content: Mapped[bytes] = mapped_column("content", LargeBinary, nullable=False, quote=False)