from uuid import UUID

from fastapi import HTTPException, status
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def ensure_all_permissions_exist(db: Session, routes: list[APIRoute]) -> None:
    for route in routes:
        for method in route.methods:
            path_parts = route.path.split("/")
            for i in range(len(path_parts)):
                permission_scope = "/" + "/".join(path_parts[1:i+1])

                if permission_scope == route.path:
                    existing_permission_scope = db.scalar(
                        select(models.PermissionScope)
                        .where(models.PermissionScope.route == permission_scope)
                        .where(models.PermissionScope.method == method)
                        .where(models.PermissionScope.isEndpoint == True)
                    )

                    if existing_permission_scope is None:
                        db.add(models.PermissionScope(
                            route=permission_scope,
                            method=method,
                            isEndpoint=True
                        ))
                        db.commit()

                existing_permission_scope = db.scalar(
                    select(models.PermissionScope)
                    .where(models.PermissionScope.route == permission_scope)
                    .where(models.PermissionScope.method == method)
                    .where(models.PermissionScope.isEndpoint == False)
                )

                if existing_permission_scope is None:
                    db.add(models.PermissionScope(
                        route=permission_scope,
                        method=method,
                        isEndpoint=False
                    ))
                    db.commit()

def prune_permissions_tree(db: Session, tree: schemas.PermissionScopeNode | None = None):
    if tree is None:
        tree = get_permissions_tree(db=db)


    if len(tree.childNodes) == 1 and tree.childNodes[0].route == tree.route:
        redundant_permission_scope_ids = tree.permissionIds.values()
        for redundant_permission_scope_id in redundant_permission_scope_ids:
            redundant_permission_scope = db.scalar(
                select(models.PermissionScope)
                .where(models.PermissionScope.id == redundant_permission_scope_id)
            )
            if redundant_permission_scope is not None:
                db.delete(redundant_permission_scope)
                db.commit()

    else:
        for child_node in tree.childNodes:
            prune_permissions_tree(db=db, tree=child_node)

def get_permissions_tree(db: Session, route_prefix: str = "", level: int = 0) -> schemas.PermissionScopeNode:

    descendant_routes_start_with = "/" + route_prefix + ("/" if route_prefix != "" else "")
    descendant_permissions = [route for route in db.scalars(
        select(models.PermissionScope)
        .distinct()
        .where(models.PermissionScope.route.startswith(descendant_routes_start_with))
    )]

    child_routes = list(set(["/".join(permission.route.split("/")[1:level+2]) for permission in descendant_permissions if permission.route != "/" + route_prefix] ) )
    child_routes.sort()

    endpoint_permission_scopes = [_ for _ in db.scalars(
        select(models.PermissionScope)
        .where(models.PermissionScope.route == "/" + route_prefix)
        .where(models.PermissionScope.isEndpoint == True)
    )]

    current_permission_scope_non_endpoint = [_ for _ in db.scalars(
        select(models.PermissionScope)
        .where(models.PermissionScope.route == "/" + route_prefix)
        .where(models.PermissionScope.isEndpoint == False)
    )]

    if len(current_permission_scope_non_endpoint) == 0:
        current_permission_scope_non_endpoint = endpoint_permission_scopes
        endpoint_permission_scopes = []


    endpoint_items = [
                       schemas.PermissionScopeNode(
                           route="/" + route_prefix,
                           permissionIds={permission.method: permission.id for permission in
                                          endpoint_permission_scopes},
                           childNodes=[]
                       )
                   ] if len(endpoint_permission_scopes) > 0 else []


    return schemas.PermissionScopeNode(
        route="/" + route_prefix,
        permissionIds={permission.method: permission.id for permission in current_permission_scope_non_endpoint},
        childNodes= endpoint_items + [get_permissions_tree(db=db, route_prefix=child_route, level=level + 1) for child_route
                                      in child_routes]
    )




def get_permission_scope(db: Session, permission_scope_id: UUID) -> models.PermissionScope:
    return db.scalar(
        select(models.PermissionScope)
        .where(models.PermissionScope.id == permission_scope_id)
    )

def get_permission_scope_by_route_and_method(db: Session, route: str, method: str) -> models.PermissionScope:
    return db.scalar(
        select(models.PermissionScope)
        .where(models.PermissionScope.route == route)
        .where(models.PermissionScope.method == method)
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

def delete_user_permission(db: Session, user_id: UUID, permission_scope_id: UUID) -> list[UUID]:

    delete_permission_scope_ids = []

    permission_scope = db.scalar(
        select(models.PermissionScope)
        .where(models.PermissionScope.id == permission_scope_id)
    )

    user_permission = get_user_permission(db=db, user_id=user_id, permission_scope_id=permission_scope_id)
    if user_permission is not None:
        delete_permission_scope_ids.append(user_permission.permissionScopeId)
        db.delete(user_permission)
        db.commit()

    child_routes_starts_with = permission_scope.route + ("/" if not permission_scope.route.endswith("/") else "")

    permission_scope_children = [_ for _ in db.scalars(
        select(models.PermissionScope)
        .where(
            (models.PermissionScope.route.startswith(child_routes_starts_with))
            & (models.PermissionScope.method == permission_scope.method)
        )
    )]

    for child in permission_scope_children:
        user_permission_child = get_user_permission(db=db, user_id=user_id, permission_scope_id=child.id)
        if user_permission_child is not None:
            delete_permission_scope_ids.append(user_permission_child.permissionScopeId)
            db.delete(user_permission_child)
            db.commit()

    return delete_permission_scope_ids


def get_user_permissions(db: Session, user_id: UUID) -> list[models.UserPermission]:
    return [_ for _ in db.scalars(
        select(models.UserPermission)
        .where(models.UserPermission.userId == user_id)
    )]

def check_user_permission(db: Session, user_id: UUID, route: str, method: str) -> bool:
    permission_scope = db.scalar(
        select(models.PermissionScope)
        .where(models.PermissionScope.route == route)
        .where(models.PermissionScope.method == method)
    )

    if permission_scope is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No permission scope found for this route and method"})
    user_permission = db.scalar(
        select(models.UserPermission)
        .where(
            (models.UserPermission.userId == user_id)
            & (models.UserPermission.permissionScopeId == permission_scope.id)
        )
    )
    return user_permission is not None