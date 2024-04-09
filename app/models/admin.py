from sqlalchemy import UUID, text, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from app.models import Client, Bike
from uuid import uuid4


class DetectedPotentialClientDuplicates(Base):
    __tablename__ = "detectedpotentialclientduplicates"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    client1Id: Mapped[UUID] = mapped_column("client1Id", ForeignKey(Client.id), nullable=False, quote=False)
    client1: Mapped[Client] = relationship(Client, foreign_keys=[client1Id])

    client2Id: Mapped[UUID] = mapped_column("client2Id", ForeignKey(Client.id), nullable=False, quote=False)
    client2: Mapped[Client] = relationship(Client, foreign_keys=[client2Id])

    similarityScore: Mapped[int] = mapped_column("similarityScore", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))

    ignore: Mapped[bool] = mapped_column("ignore", Boolean, default=False, server_default=text("FALSE"),
                                              nullable=False, quote=False)


class DetectedPotentialBikeDuplicates(Base):
    __tablename__ = "detectedpotentialbikeduplicates"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    bike1Id: Mapped[UUID] = mapped_column("bike1Id", ForeignKey(Bike.id), nullable=False, quote=False)
    bike1: Mapped[Bike] = relationship(Bike, foreign_keys=[bike1Id])

    bike2Id: Mapped[UUID] = mapped_column("bike2Id", ForeignKey(Bike.id), nullable=False, quote=False)
    bike2: Mapped[Bike] = relationship(Bike, foreign_keys=[bike2Id])

    similarityScore: Mapped[int] = mapped_column("similarityScore", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))

    ignore: Mapped[bool] = mapped_column("ignore", Boolean, default=False, server_default=text("FALSE"),
                                              nullable=False, quote=False)
