from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

import app.models as models
import app.schemas as schemas
from .permissions import get_permission
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


def add_permission_to_group(db: Session, group_id: UUID, permission_id: UUID) -> schemas.GroupPermission:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    permission_scope = get_permission(db=db, permission_id=permission_id)
    if permission_scope is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})
    group.permissions.append(permission_scope)
    db.commit()
    return schemas.GroupPermission(
        permissionId=permission_scope.id,
        groupId=group.id
    )


def remove_permission_from_group(db: Session, group_id: UUID, permission_id: UUID) -> list[UUID]:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    permission = get_permission(db=db, permission_id=permission_id)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})

    delete_permission_ids = []

    if permission in group.permissions:
        group.permissions.remove(permission)
        delete_permission_ids.append(permission.id)
        db.commit()

    child_routes_starts_with = permission.route + ("/" if not permission.route.endswith("/") else "")

    permission_children = [_ for _ in db.scalars(
        select(models.Permission)
        .where(
            (models.Permission.route.startswith(child_routes_starts_with))
            & (models.Permission.method == permission.method)
        )
    )]

    for child in permission_children:
        if child in group.permissions:
            delete_permission_ids.append(child.id)
            group.permissions.remove(child)
            db.commit()

    return delete_permission_ids


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

def create_group(db: Session, group_name: str) -> schemas.Group:
    group = models.Group(
        name=group_name
    )
    db.add(group)
    db.commit()
    return group

def delete_group(db: Session, group_id: UUID) -> schemas.Group:
    group = get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    schema = schemas.Group(
        id=group.id,
        name=group.name
    )
    db.delete(group)
    db.commit()
    return schema
