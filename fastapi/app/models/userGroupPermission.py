from uuid import uuid4

from sqlalchemy import UUID, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class UserGroupPermission(Base):
    __tablename__ = "usergrouppermissions"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    userGroupId: Mapped[UUID] = mapped_column("usergroupid", ForeignKey("usergroups.id"), nullable=False, quote=False)
    userGroup: Mapped["UserGroup"] = relationship("UserGroup", back_populates="userGroupPermissions")

    permissionScopeId: Mapped[UUID] = mapped_column("permissionscopeid", ForeignKey("permissionscopes.id"), nullable=False, quote=False)
    permissionScope: Mapped["PermissionScope"] = relationship("PermissionScope", back_populates="userGroupPermissions")
