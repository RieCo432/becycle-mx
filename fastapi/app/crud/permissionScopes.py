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

    current_route = route_prefix + "/"
    descendant_routes = [route for route in db.scalars(
        select(models.PermissionScope.route)
        .distinct()
        .where(models.PermissionScope.route.startswith(current_route))
    )]

    child_routes = list(set(["/".join(route.split("/")[:level+2]) for route in descendant_routes if route != current_route] ) )

    return schemas.PermissionScopeNode(
        route=route_prefix,
        permissionIds={permission.method: permission.id for permission in db.scalars(
            select(models.PermissionScope)
            .where(models.PermissionScope.route == current_route)
        )},
        child_nodes=[get_permission_scopes(db=db, route_prefix=child_route, level=level + 1) for child_route in child_routes]
    )
