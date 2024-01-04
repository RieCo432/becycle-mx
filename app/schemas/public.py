from pydantic import BaseModel
from datetime import time


class DayOpeningTimes(BaseModel):
    day: str
    open: str
    close: str
