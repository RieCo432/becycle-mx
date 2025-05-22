from sqlalchemy import ForeignKey, Table, Column
from app.database.db import Base


group_user_association_table = Table(
    "groupusers",
    Base.metadata,
    Column("groupid", ForeignKey("groups.id"), primary_key=True),
    Column("userid", ForeignKey("users.id"), primary_key=True),
)
