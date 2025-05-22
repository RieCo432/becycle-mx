from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

import app.models as models
import app.schemas as schemas
from .permissionScopes import get_permission_scope
from .users import get_user


def get_group(db: Session, group_id: UUID) -> models.Group:
    return db.scalar(
        select(models.Group)
        .where(models.Group.id == group_id)
    )

def get_groups(db: Session) -> list[models.Group]:
    return [_ for _ in db.scalars(
        select(models.Group)
    )]


def add_permission_to_group(db: Session, group_id: UUID, permission_scope_id: UUID) -> schemas.GroupPermission:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    permission_scope = get_permission_scope(db=db, permission_scope_id=permission_scope_id)
    if permission_scope is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})
    group.permissions.append(permission_scope)
    db.commit()
    return schemas.GroupPermission(
        permissionScopeId=permission_scope.id,
        groupId=group.id
    )


def remove_permission_from_group(db: Session, group_id: UUID, permission_scope_id: UUID) -> list[UUID]:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    permission_scope = get_permission_scope(db=db, permission_scope_id=permission_scope_id)
    if permission_scope is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"description": "This functionality is not yet implemented. Please contact the administrator. Thank you."})


def remove_user_from_group(db: Session, group_id: UUID, user_id: UUID) -> schemas.User:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    group.users.remove(user)
    db.commit()
    return user


def add_user_to_group(db: Session, group_id: UUID, user_id: UUID) -> schemas.GroupUser:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    group.users.append(user)
    db.commit()
    return schemas.GroupUser(
        userId=user.id,
        groupId=group.id
    )