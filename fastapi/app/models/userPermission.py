from sqlalchemy import ForeignKey, Table, Column
from app.database.db import Base


user_permission_association_table = Table(
    "userpermissions",
    Base.metadata,
    Column("userid", ForeignKey("users.id"), primary_key=True),
    Column("permissionid", ForeignKey("permissions.id"), primary_key=True),
)