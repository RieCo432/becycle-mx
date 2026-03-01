from typing import List
from uuid import uuid4

from datetime import datetime, timezone
from sqlalchemy import String, UUID, text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base



class SaleHeader(Base):
    __tablename__ = "saleheaders"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    createdOn: Mapped[datetime] = mapped_column("createdon", DateTime, nullable=False, default=datetime.now(timezone.utc), server_default=text("(current_timestamp at time zone 'utc')"), quote=False)
    createdByUserId: Mapped[UUID] = mapped_column("createdbyuserid", ForeignKey("users.id"), nullable=False, quote=False)
    createdByUser: Mapped["User"] = relationship("User", foreign_keys=[createdByUserId], back_populates="saleHeadersCreated")

    transactionHeaderId: Mapped[UUID] = mapped_column("transactionheaderid", ForeignKey("transactionheaders.id"), nullable=True, quote=False)
    transactionHeader: Mapped["TransactionHeader"] = relationship("TransactionHeader", foreign_keys=[transactionHeaderId])

    catalogueItemSaleLines: Mapped[List["CatalogueItemSaleLine"]] = relationship("CatalogueItemSaleLine", back_populates="saleHeader")
    bikeSaleLines: Mapped[List["BikeItemSaleLine"]] = relationship("BikeSaleLine", back_populates="saleHeader")
    
    
    
class CatalogueItemSaleLine(Base):
    __tablename__ = "catalogueitemsalelines"
    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    saleHeaderId: Mapped[UUID] = mapped_column("saleheaderid", ForeignKey("saleheaders.id"), nullable=False, quote=False)
    saleHeader: Mapped[SaleHeader] = relationship("SaleHeader", foreign_keys=[saleHeaderId], back_populates="saleLines")
    
    quantity: Mapped[int] = mapped_column("quantity", Integer, nullable=False, quote=False)
    salePrice: Mapped[int] = mapped_column("saleprice", Integer, nullable=False, quote=False)
    
    catalogueItemId: Mapped[UUID] = mapped_column("catalogueitemid", ForeignKey("catalogueitems.id"), nullable=False, quote=False)
    catalogueItem: Mapped["CatalogueItem"] = relationship("CatalogueItem", foreign_keys=[catalogueItemId], back_populates="saleLines")
    
    
class BikeSaleLine(Base):
    __tablename__ = "bikesalelines"
    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    saleHeaderId: Mapped[UUID] = mapped_column("saleheaderid", ForeignKey("saleheaders.id"), nullable=False, quote=False)
    saleHeader: Mapped[SaleHeader] = relationship("SaleHeader", foreign_keys=[saleHeaderId], back_populates="saleLines")
    
    salePrice: Mapped[int] = mapped_column("saleprice", Integer, nullable=False, quote=False)
    
    bikeId: Mapped[UUID] = mapped_column("bikeid", ForeignKey("bikes.id"), nullable=False, quote=False)
    bike: Mapped["Bike"] = relationship("Bike", foreign_keys=[bikeId], back_populates="saleLines")