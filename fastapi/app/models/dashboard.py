from uuid import uuid4

from sqlalchemy import String, UUID, text, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, nullable=False, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    name: Mapped[str] = mapped_column("name", String(64), nullable=False, quote=False)
    layout: Mapped[str] = mapped_column("queries", Text, nullable=False, quote=False)
    index: Mapped[int] = mapped_column("index", Integer, unique=True, nullable=False, quote=False, autoincrement=True)