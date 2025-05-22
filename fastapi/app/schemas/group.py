from pydantic import BaseModel
from uuid import UUID


class Group(BaseModel):
    id: UUID
    name: str


class GroupCreate(BaseModel):
    name: str


class GroupPermission(BaseModel):
    permissionId: UUID
    groupId: UUID


class GroupUser(BaseModel):
    userId: UUID
    groupId: UUID
