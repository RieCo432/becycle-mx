import os
from datetime import datetime, date
from typing import List
from uuid import uuid4

from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from .userGroupPermission import UserGroupPermission
from .userGroupUser import UserGroupUser



class UserGroup(Base):
    __tablename__ = "usergroups"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    name: Mapped[str] = mapped_column("name", Text, nullable=False, quote=False)

    userGroupPermissions: Mapped[List["UserGroupPermission"]] = relationship("UserGroupPermission",
                                                                             foreign_keys=[
                                                                                 UserGroupPermission.userGroupId],
                                                                             back_populates="userGroup")

    users: Mapped[List["UserGroupUser"]] = relationship("UserGroupUser",
                                                                             foreign_keys=[
                                                                                 UserGroupUser.userGroupId],
                                                                             back_populates="userGroup")

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.name) == str(other.get("name"))
        ])
