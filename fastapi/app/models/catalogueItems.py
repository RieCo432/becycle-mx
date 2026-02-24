from typing import List
from uuid import uuid4

from datetime import datetime
from sqlalchemy import String, UUID, text, DateTime, LargeBinary, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class CatalogueItem(Base):
    __tablename__ = "catalogueitems"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    name: Mapped[str] = mapped_column("make", String(60), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", String(512), nullable=True, quote=False)
    photoId: Mapped[UUID] = mapped_column("photoid", ForeignKey("catalogueitemphotos.id"), nullable=True, quote=False)
    photo: Mapped["CatalogueItemPhoto"] = relationship("CatalogueItemPhoto")
    purchasePrice: Mapped[int] = mapped_column("purchaseprice", Integer, nullable=True, quote=False)
    recommendedRetailPrice: Mapped[int] = mapped_column("recommendedretailprice", Integer, nullable=True, quote=False)

    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.utcnow(), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)


class CatalogueItemPhoto(Base):
    __tablename__ = "catalogueitemphotos"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)

    contentType: Mapped[str] = mapped_column("photocontenttype", Text, nullable=True, quote=False)
    content: Mapped[bytes] = mapped_column("content", LargeBinary, nullable=False, quote=False)