from sqlalchemy import ForeignKey, Table, Column
from app.database.db import Base


bike_colour_association_table = Table(
    "bikecolours",
    Base.metadata,
    Column("bikeid", ForeignKey("bikes.id"), primary_key=True),
    Column("colourid", ForeignKey("colours.id"), primary_key=True),
)
