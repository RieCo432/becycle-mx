from __future__ import annotations
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionScopeRoute(BaseModel):
    routePart: str
    methods: list[PermissionScopeNode]

class PermissionScopeNode(BaseModel):
    route: str
    permissionIds: dict[str, UUID]
    childNodes: list[PermissionScopeNode] | None

class UserPermission(BaseModel):
    id: UUID
    userId: UUID
    permissionScopeId: UUID

class PermissionScope(BaseModel):
    id: UUID
    method: str
    route: str
    isEndpoint: bool

class NewUserPermission(BaseModel):
    permissionScopeId: UUID

