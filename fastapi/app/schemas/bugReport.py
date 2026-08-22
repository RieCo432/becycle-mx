from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID

class BugReport(BaseModel):
    id: UUID
    reportedByUserId: UUID
    reportedByUserName: str
    reportedAt: datetime
    pageAddress: str
    description: str
    consoleHistory: str

    model_config = ConfigDict(from_attributes=True)

class BugReportCreate(BaseModel):
    pageAddress: str
    description: str
    consoleHistory: str

class BugReportUpdate(BaseModel):
    description: str
