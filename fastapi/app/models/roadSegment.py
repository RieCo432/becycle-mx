from datetime import datetime
from uuid import uuid4

from sqlalchemy import text, Text, Integer, UUID, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class RoadSegment(Base):
    __tablename__ = "roadsegments"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    fromLatitude: Mapped[float] = mapped_column("fromlatitude", Float, nullable=False, quote=False, index=True)
    fromLongitude: Mapped[float] = mapped_column("fromlongitude", Float, nullable=False, quote=False, index=True)
    toLatitude: Mapped[float] = mapped_column("tolatitude", Float, nullable=False, quote=False, index=True)
    toLongitude: Mapped[float] = mapped_column("tolongitude", Float, nullable=False, quote=False, index=True)

    roadClassification: Mapped[str] = mapped_column("roadclassification", Text, default=None,
                                                 server_default=text("NULL"), nullable=True,
                                                 quote=False)
    roadFunction: Mapped[str] = mapped_column("roadfunction", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    formOfWay: Mapped[str] = mapped_column("formofway", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    name: Mapped[str] = mapped_column("name", Text, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False)
    length: Mapped[int] = mapped_column("length", Integer, default=None,
                                                    server_default=text("NULL"), nullable=True,
                                                    quote=False, index=True)


class RoadSegmentReportType(Base):
    __tablename__ = "roadsegmentreporttypes"
    id: Mapped[str] = mapped_column("id", String(5), primary_key=True, nullable=False, index=True, quote=False)
    title: Mapped[str] = mapped_column("title", String(40), nullable=False, quote=False)
    description: Mapped[str] = mapped_column("description", Text, nullable=False, quote=False)
    scoreModifier: Mapped[int] = mapped_column("scoremodifier", Integer, nullable=False, quote=False)

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.title) == str(other.get("title")),
            str(self.description) == str(other.get("description")),
            str(self.scoreModifier) == str(other.get("scoreModifier")),
        ])


class RoadSegmentReport(Base):
    __tablename__ = "roadsegmentreports"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4,
                                     server_default=text("uuid_generate_v4()"), index=True, quote=False)
    datetime: Mapped[datetime] = mapped_column("datetime", DateTime, nullable=False, quote=False, default=datetime.utcnow(), server_default=text("current_timestamp"))

    roadSegmentId: Mapped[UUID] = mapped_column("roadsegmentid", ForeignKey(RoadSegment.id), nullable=False, quote=False)
    roadSegment: Mapped[RoadSegment] = relationship(RoadSegment)

    typeId: Mapped[str] = mapped_column("typeid", ForeignKey(RoadSegmentReportType.id), nullable=False, quote=False)
    type: Mapped[RoadSegmentReportType] = relationship(RoadSegmentReportType)




