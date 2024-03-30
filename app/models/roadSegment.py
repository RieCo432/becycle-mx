from sqlalchemy import text, Text, Integer, UUID, Float
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from app.database.db import Base


class RoadSegment(Base):
    __tablename__ = "roadsegments"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    fromLatitude: Mapped[float] = mapped_column("fromLatitude", Float, nullable=False, quote=False, index=True)
    fromLongitude: Mapped[float] = mapped_column("fromLongitude", Float, nullable=False, quote=False, index=True)
    toLatitude: Mapped[float] = mapped_column("toLatitude", Float, nullable=False, quote=False, index=True)
    toLongitude: Mapped[float] = mapped_column("toLongitude", Float, nullable=False, quote=False, index=True)

    roadClassification: Mapped[str] = mapped_column("roadClassification", Text, default=None,
                                                 server_default=text("NULL"), nullable=True,
                                                 quote=False)
    roadFunction: Mapped[str] = mapped_column("roadFunction", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    formOfWay: Mapped[str] = mapped_column("formOfWay", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    name: Mapped[str] = mapped_column("name", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    length: Mapped[int] = mapped_column("length", Integer, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False, index=True)




