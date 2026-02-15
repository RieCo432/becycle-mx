from __future__ import annotations
import os
from datetime import datetime, date
from typing import List
from uuid import uuid4

from sqlalchemy import String, UUID, text, ForeignKey, Date, Integer, Text, Boolean, LargeBinary, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from . import group_user_association_table, Permission
from .groupPermission import group_permission_association_table
from .accounts import Account



class Group(Base):
    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    name: Mapped[str] = mapped_column("name", Text, nullable=False, quote=False)

    permissions: Mapped[List["Permission"]] = relationship(secondary=group_permission_association_table, back_populates="groups")

    users: Mapped[List["User"]] = relationship(secondary=group_user_association_table, back_populates="groups")

    accountsOwned: Mapped[List["Account"]] = relationship("Account", foreign_keys=[Account.ownerGroupId], back_populates="ownerGroup")

    def __eq__(self, other: dict):
        return all([
            str(self.id) == str(other.get("id")),
            str(self.name) == str(other.get("name"))
        ])
