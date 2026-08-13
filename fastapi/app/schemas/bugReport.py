from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

class BugReport(BaseModel):
    id: UUID
    reportedByUserId: UUID
    reportedAt: datetime
    pageAddress: str
    description: str
    consoleHistory: str

class BugReportCreate(BaseModel):
    pageAddress: str
    description: str
    consoleHistory: str

class BugReportUpdate(BaseModel):
    description: str
