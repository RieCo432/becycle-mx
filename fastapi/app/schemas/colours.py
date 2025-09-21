from pydantic import BaseModel


class ColourBase(BaseModel):
    hex: str


class Colour(ColourBase):
    name: str