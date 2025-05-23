from __future__ import annotations
import os
from datetime import datetime, date
from typing import List
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

from .userPermission import user_permission_association_table
from .groupPermission import group_permission_association_table


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    route: Mapped[str] = mapped_column("route", Text, nullable=False, quote=False)
    method: Mapped[str] = mapped_column("method", Text, nullable=False, quote=False)
    isEndpoint: Mapped[bool] = mapped_column("isendpoint", Boolean, nullable=False, default=False, server_default=text("FALSE"), quote=False)
    parentPermissionId = mapped_column("parentpermissionid", ForeignKey("permissions.id"), nullable=True, quote=False)
    parentPermission: Mapped["Permission"] = relationship("Permission", remote_side=[id], back_populates="childPermissions")
    childPermissions: Mapped[List[Permission]] = relationship("Permission", back_populates="parentPermission")

    users: Mapped[List["User"]] = relationship(secondary=user_permission_association_table, back_populates="permissions")
    groups: Mapped[List["Group"]] = relationship(secondary=group_permission_association_table, back_populates="permissions")

    def __eq__(self, other: Permission):
        return all([
            self.id == other.id,
            self.route == other.route,
            self.method == other.method
        ])

    # def __eq__(self, other: dict):
    #     return all([
    #         str(self.id) == str(other.get("id")),
    #         str(self.route) == str(other.get("route")),
    #         str(self.method) == str(other.get("method"))
    #     ])
