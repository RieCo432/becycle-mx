from __future__ import annotations
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionRoute(BaseModel):
    routePart: str
    methods: list[PermissionNode]

class PermissionNode(BaseModel):
    route: str
    permissionIds: dict[str, UUID]
    childNodes: list[PermissionNode] | None

class UserPermission(BaseModel):
    userId: UUID
    permissionId: UUID

class Permission(BaseModel):
    id: UUID
    method: str
    route: str
    isEndpoint: bool

class NewUserPermission(BaseModel):
    permissionId: UUID

