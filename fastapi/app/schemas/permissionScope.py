from __future__ import annotations
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionScopeRoute(BaseModel):
    routePart: str
    methods: list[PermissionScopeNode]

class PermissionScopeNode(BaseModel):
    route: str
    permissionIds: dict[str, UUID]
    child_nodes: list[PermissionScopeNode] | None


