from uuid import uuid4

from sqlalchemy import UUID, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class UserGroupUser(Base):
    __tablename__ = "usergroupusers"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    userId: Mapped[UUID] = mapped_column("userid", ForeignKey("users.id"), nullable=False, quote=False)
    user: Mapped["User"] = relationship("User", back_populates="groups")

    userGroupId: Mapped[UUID] = mapped_column("usergroupid", ForeignKey("usergroups.id"), nullable=False, quote=False)
    userGroup: Mapped["UserGroup"] = relationship("UserGroup", back_populates="users")
