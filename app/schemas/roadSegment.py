from pydantic import BaseModel, ConfigDict
from uuid import UUID


class RoadSegmentReportType(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    scoreModifier: int


class NewRoadSegmentReport(BaseModel):
    roadSegmentId: UUID
    roadSegmentReportTypeId: str
