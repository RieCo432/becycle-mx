from uuid import UUID

from fastapi import HTTPException, status
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.crud import get_user


def ensure_all_permissions_exist(db: Session, routes: list[APIRoute]) -> None:
    for route in routes:
        for method in route.methods:
            path_parts = route.path.split("/")
            parent_permission_id = None
            for i in range(len(path_parts)):
                permission_scope = "/" + "/".join(path_parts[1:i+1])

                parent_permission = db.scalar(
                    select(models.Permission)
                    .where(models.Permission.route == permission_scope)
                    .where(models.Permission.method == method)
                    .where(models.Permission.isEndpoint == False)
                )

                if parent_permission is None:
                    parent_permission = models.Permission(
                        route=permission_scope,
                        method=method,
                        isEndpoint=False,
                        parentPermissionId=parent_permission_id,
                    )
                    db.add(parent_permission)
                    db.commit()


                if permission_scope == route.path:
                    parent_permission = db.scalar(
                        select(models.Permission)
                        .where(models.Permission.route == permission_scope)
                        .where(models.Permission.method == method)
                        .where(models.Permission.isEndpoint == True)
                    )

                    if parent_permission is None:
                        db.add(models.Permission(
                            route=permission_scope,
                            method=method,
                            isEndpoint=True,
                            parentPermissionId=parent_permission_id,
                        ))
                        db.commit()
                
                else:
                    parent_permission_id = parent_permission.id

def prune_permissions_tree(db: Session, tree: schemas.PermissionNode | None = None):
    if tree is None:
        tree = get_permissions_tree(db=db)


    if len(tree.childNodes) == 1 and tree.childNodes[0].route == tree.route:
        redundant_permission_scope_ids = tree.permissionIds.values()
        for redundant_permission_scope_id in redundant_permission_scope_ids:
            redundant_permission_scope = db.scalar(
                select(models.Permission)
                .where(models.Permission.id == redundant_permission_scope_id)
            )
            if redundant_permission_scope is not None:
                db.delete(redundant_permission_scope)
                db.commit()

    else:
        for child_node in tree.childNodes:
            prune_permissions_tree(db=db, tree=child_node)

def get_permissions_tree(db: Session, route_prefix: str = "", level: int = 0) -> schemas.PermissionNode:

    descendant_routes_start_with = "/" + route_prefix + ("/" if route_prefix != "" else "")
    descendant_permissions = [route for route in db.scalars(
        select(models.Permission)
        .distinct()
        .where(models.Permission.route.startswith(descendant_routes_start_with))
    )]

    child_routes = list(set(["/".join(permission.route.split("/")[1:level+2]) for permission in descendant_permissions if permission.route != "/" + route_prefix] ) )
    child_routes.sort()

    endpoint_permission = [_ for _ in db.scalars(
        select(models.Permission)
        .where(models.Permission.route == "/" + route_prefix)
        .where(models.Permission.isEndpoint == True)
    )]

    current_permission_non_endpoint = [_ for _ in db.scalars(
        select(models.Permission)
        .where(models.Permission.route == "/" + route_prefix)
        .where(models.Permission.isEndpoint == False)
    )]

    if len(current_permission_non_endpoint) == 0:
        current_permission_non_endpoint = endpoint_permission
        endpoint_permission = []


    endpoint_items = [
                       schemas.PermissionNode(
                           route="/" + route_prefix,
                           permissionIds={permission.method: permission.id for permission in
                                          endpoint_permission},
                           childNodes=[]
                       )
                   ] if len(endpoint_permission) > 0 else []


    return schemas.PermissionNode(
        route="/" + route_prefix,
        permissionIds={permission.method: permission.id for permission in current_permission_non_endpoint},
        childNodes= endpoint_items + [get_permissions_tree(db=db, route_prefix=child_route, level=level + 1) for child_route
                                      in child_routes]
    )




def get_permission(db: Session, permission_id: UUID) -> models.Permission:
    return db.scalar(
        select(models.Permission)
        .where(models.Permission.id == permission_id)
    )

def get_permission_by_route_and_method(db: Session, route: str, method: str) -> models.Permission:
    return db.scalar(
        select(models.Permission)
        .where(models.Permission.route == route)
        .where(models.Permission.method == method)
    )

def add_user_permission(db: Session, user_id: UUID, permission_id: UUID) -> schemas.UserPermission:
    permission = get_permission(db=db, permission_id=permission_id)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission not found"})
    
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    
    user.permissions.append(permission)
    db.commit()

    return schemas.UserPermission(
        userId=user_id,
        permissionId=permission_id
    )

def delete_user_permission(db: Session, user_id: UUID, permission_scope_id: UUID) -> list[UUID]:

    deleted_permission_ids = []

    permission = get_permission(db=db, permission_id=permission_scope_id)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission not found"})

    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})

    if permission not in user.permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User does not have permission"})
    user.permissions.remove(permission)
    db.commit()

    deleted_permission_ids.append(permission.id)


    child_routes_starts_with = permission.route + ("/" if not permission.route.endswith("/") else "")

    permission_scope_children = [_ for _ in db.scalars(
        select(models.Permission)
        .where(
            (models.Permission.route.startswith(child_routes_starts_with))
            & (models.Permission.method == permission.method)
        )
    )]

    for child in permission_scope_children:
        child_permission = get_permission(db=db, permission_id=child.id)
        if child_permission is not None:
            if child_permission in user.permissions:
                user.permissions.remove(child_permission)
                db.commit()
                deleted_permission_ids.append(child_permission.id)

    return deleted_permission_ids


def check_user_permission(db: Session, user_id: UUID, route: str, method: str) -> bool:
    permission = db.scalar(
        select(models.Permission)
        .where(models.Permission.route == route)
        .where(models.Permission.method == method)
    )

    if permission is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No permission scope found for this route and method"})

    user = get_user(db=db, user_id=user_id)
    if user is not None:
        return permission in user.permissions

    return False