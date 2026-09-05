from uuid import UUID
from pydantic import BaseModel, ConfigDict



class DashboardBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    layout: str
    index: int | None = None
    
    
class DashboardCreate(DashboardBase):
    pass


class Dashboard(DashboardBase):
    id: UUID

    