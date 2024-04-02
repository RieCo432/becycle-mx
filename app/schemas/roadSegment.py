from pydantic import BaseModel, ConfigDict


class RoadSegmentReportType(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    scoreModifier: int
