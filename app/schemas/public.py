from pydantic import BaseModel


class DayOpeningTimes(BaseModel):
    day: str
    open: str
    close: str
