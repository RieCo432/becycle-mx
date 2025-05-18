import os
from datetime import datetime
from uuid import UUID

import bcrypt
from fastapi import HTTPException, status, UploadFile
from fastapi.routing import APIRoute
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.routing import BaseRoute

import app.models as models
import app.schemas as schemas


def ensure_all_permissions_exist(db: Session, routes: list[APIRoute]) -> None:
    for route in routes:
        for method in route.methods:
            path_parts = route.path.split("/")
            for i in range(len(path_parts)):
                permission_scope = "/" + "/".join(path_parts[1:i+1])

                existing_permission_scope = db.scalar(
                    select(models.PermissionScope)
                    .where(models.PermissionScope.route == permission_scope)
                    .where(models.PermissionScope.method == method)
                )

                if existing_permission_scope is None:
                    new_permission_scope = models.PermissionScope(
                        route=permission_scope,
                        method=method
                    )
                    db.add(new_permission_scope)
                    db.commit()

def get_permission_scopes(db: Session, route_prefix: str = "", level: int = 0) -> schemas.PermissionScopeNode:

    descendant_routes_start_with = "/" + route_prefix + ("/" if route_prefix != "" else "")
    descendant_routes = [route for route in db.scalars(
        select(models.PermissionScope.route)
        .distinct()
        .where(models.PermissionScope.route.startswith(descendant_routes_start_with))
    )]

    child_routes = list(set(["/".join(route.split("/")[1:level+2]) for route in descendant_routes if route != "/" + route_prefix] ) )

    return schemas.PermissionScopeNode(
        route="/" + route_prefix,
        permissionIds={permission.method: permission.id for permission in db.scalars(
            select(models.PermissionScope)
            .where(models.PermissionScope.route == "/" + route_prefix)
        )},
        childNodes=[get_permission_scopes(db=db, route_prefix=child_route, level=level + 1) for child_route in child_routes]
    )

def get_permission_scope(db: Session, permission_scope_id: UUID) -> models.PermissionScope:
    return db.scalar(
        select(models.PermissionScope)
        .where(models.PermissionScope.id == permission_scope_id)
    )

def get_user_permission(db: Session, user_id: UUID, permission_scope_id: UUID) -> models.UserPermission:
    return db.scalar(
        select(models.UserPermission)
        .where(
            (models.UserPermission.userId == user_id)
            & (models.UserPermission.permissionScopeId == permission_scope_id)
        )
    )

def add_user_permission(db: Session, user_id: UUID, permission_scope_id: UUID) -> models.UserPermission:
    user_permission = models.UserPermission(
        userId=user_id,
        permissionScopeId=permission_scope_id
    )
    db.add(user_permission)
    db.commit()

    return user_permission

def delete_user_permission(db: Session, user_id: UUID, permission_scope_id: UUID) -> None:
    user_permission = db.scalar(
        select(models.UserPermission)
        .where(
            (models.UserPermission.userId == user_id)
            & (models.UserPermission.permissionScopeId == permission_scope_id)
        )
    )
    db.delete(user_permission)
    db.commit()

def get_user_permissions(db: Session, user_id: UUID) -> list[models.UserPermission]:
    return [_ for _ in db.scalars(
        select(models.UserPermission)
        .where(models.UserPermission.userId == user_id)
    )]
