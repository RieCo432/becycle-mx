from sqlalchemy import ForeignKey, Table, Column
from app.database.db import Base


group_permission_association_table = Table(
    "grouppermissions",
    Base.metadata,
    Column("groupid", ForeignKey("groups.id"), primary_key=True),
    Column("permissionid", ForeignKey("permissions.id"), primary_key=True),
)
