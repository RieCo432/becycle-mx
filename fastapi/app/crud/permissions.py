from uuid import UUID

import bcrypt
from fastapi import HTTPException, status
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from .users import get_user
from app.models import User, Permission, Group


def ensure_all_permissions_exist(db: Session, routes: list[APIRoute]) -> None:
    for route in routes:
        for method in route.methods:
            path_parts = route.path.split("/")
            parent_permission = None

            endpoint_permission = db.scalar(
                select(models.Permission)
                .where(models.Permission.route == route.path)
                .where(models.Permission.method == method)
                .where(models.Permission.isEndpoint == True)
            )

            if endpoint_permission is None:

                for i in range(len(path_parts)):
                    permission_scope = "/" + "/".join(path_parts[1:i+1])

                    existing_permission = db.scalar(
                        select(models.Permission)
                        .where(models.Permission.route == permission_scope)
                        .where(models.Permission.method == method)
                        .where(models.Permission.isEndpoint == False)
                    )

                    if existing_permission is None:
                        existing_permission = models.Permission(
                            route=permission_scope,
                            method=method,
                            isEndpoint=False,
                            parentPermissionId=parent_permission.id if parent_permission is not None else None,
                        )
                        db.add(existing_permission)
                        db.commit()

                    parent_permission = existing_permission


                db.add(models.Permission(
                    route=route.path,
                    method=method,
                    isEndpoint=True,
                    parentPermissionId=parent_permission.id,
                ))
                db.commit()


def get_num_permissions(db: Session) -> int:
    return len([_ for _ in db.scalars(select(models.Permission))])


def fully_prune_tree(db: Session) -> None:
    num_permissions = get_num_permissions(db=db)
    prune_permissions_tree(db=db, tree=get_permissions_tree(db=db))
    while num_permissions > (num_permissions := get_num_permissions(db=db)):
        prune_permissions_tree(db=db, tree=get_permissions_tree(db=db))


def prune_permissions_tree(db: Session, tree: schemas.PermissionNode) -> None:
    if tree is None:
        return

    if len(tree.childNodes) == 0:
        return

    permissions = [db.scalar(select(models.Permission).where(models.Permission.id == permission_id)) for permission_id in tree.permissionIds.values()]

    if len(tree.childNodes) == 1:
        if not any([permission.isEndpoint for permission in permissions]):
            child_node = tree.childNodes[0]
            child_permissions = [db.scalar(select(models.Permission).where(models.Permission.id == child_permission_id)) for child_permission_id in child_node.permissionIds.values()]
            if all([child_permission.isEndpoint for child_permission in child_permissions]):
                for child_permission in child_permissions:
                    parent_permission = child_permission.parentPermission
                    grandparent_permission = parent_permission.parentPermission
                    child_permission.parentPermissionId = grandparent_permission.id
                    db.commit()
                    db.delete(parent_permission)
                    db.commit()

    for child_node in tree.childNodes:
        prune_permissions_tree(db=db, tree=child_node)

    return


def delete_permission(db: Session, permission: models.Permission) -> None:
    for child_permission in permission.childPermissions:
        delete_permission(db=db, permission=child_permission)
    db.commit()
    db.delete(permission)
    db.commit()


def remove_permissions_for_nonexistent_routes(db: Session, routes: list[APIRoute]) -> None:
    permissions = db.scalars(select(models.Permission)).all()
    for permission in permissions:
        matching_routes = [route for route in routes if route.path.startswith(permission.route) and permission.method in route.methods]
        if len(matching_routes) == 0:
            delete_permission(db=db, permission=permission)


def ensure_default_admin_permissions_exist(db: Session) -> None:
    admin_user = db.scalar(select(models.User).where(models.User.username == "admin"))

    if admin_user is None:
        admin_user = models.User(
            username="admin",
            password=bcrypt.hashpw("admin", bcrypt.gensalt()),
            rentalChecker=True,
            softDeleted=False
        )
        db.add(admin_user)
        db.commit()

    admin_group = db.scalar(select(models.Group).where(models.Group.name == "admin"))



    if admin_group is None:
        admin_group = models.Group(name="admin")
        db.add(admin_group)
        db.commit()

    if admin_group not in admin_user.groups:
        admin_user.groups.append(admin_group)
        db.commit()

    global_permissions = [_ for _ in db.scalars(select(models.Permission).where(models.Permission.route == "/"))]
    for p in global_permissions:
        if p not in admin_group.permissions:
            admin_group.permissions.append(p)
            db.commit()


def get_permissions_tree(db: Session, route: str = "/", is_leaf: bool = False) -> schemas.PermissionNode:

    query = select(models.Permission).where(models.Permission.route == route)

    if is_leaf:
        query = query.where(models.Permission.isEndpoint == True)

    permissions = [_ for _ in db.scalars(query)]

    child_elements = []

    for permission in permissions:
        for child in permission.childPermissions:
            if child.route not in [e["route"] for e in child_elements]:
                child_elements.append({"is_leaf": child.isEndpoint, "route": child.route})

    child_elements.sort(key=lambda element: element["route"])

    child_nodes = []

    for child_element in child_elements:
        child_tree = get_permissions_tree(db=db, route=child_element["route"], is_leaf=(child_element["route"] == route) or child_element["is_leaf"])
        child_nodes.append(child_tree)


    permission_ids = {permission.method: permission.id for permission in permissions if permission.isEndpoint == is_leaf}


    return schemas.PermissionNode(
        route=permissions[0].route,
        permissionIds=permission_ids,
        childNodes=child_nodes
    )


def get_permission(db: Session, permission_id: UUID) -> models.Permission:
    return db.scalar(
        select(models.Permission)
        .where(models.Permission.id == permission_id)
    )

def get_permission_by_route_and_method(db: Session, route: str, method: str) -> models.Permission:
    endpoint_permission = db.scalar(
        select(models.Permission)
        .where(models.Permission.route == route)
        .where(models.Permission.method == method)
        .where(models.Permission.isEndpoint == True)
    )

    if endpoint_permission is not None:
        return endpoint_permission

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

    if permission in user.permissions:
        deleted_permission_ids.append(permission.id)
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


def _collect_endpoint_leaves(node: Permission, visited: set, out: list) -> None:
    """Recursively collect every endpoint (leaf) node at or below `node`.

    Granting a scope (a non-endpoint parent) grants all of its endpoint
    descendants; this mirrors the 'walk up to an ancestor' logic used by
    ``check_permission`` when enforcing access on the server side.
    """
    if node.id in visited:
        return
    visited.add(node.id)
    if node.isEndpoint:
        out.append(node)
    for child in node.childPermissions:
        _collect_endpoint_leaves(child, visited, out)


def get_user_allowed_endpoints(db: Session, user: User) -> list[Permission]:
    """Return the set of endpoint permissions a user may call.

    The union of the user's own grants and every grant held by a group the
    user belongs to, each expanded to its endpoint leaves. This is the
    client-facing, materialized form of the same decision the server makes
    in ``check_permissions`` — so the frontend can gate UI (``can``) without
    re-implementing/ duplicating the authorization logic. The server remains
    the enforcement boundary.
    """
    holders = [user, *user.groups]
    allowed: list[Permission] = []
    seen = set()
    for holder in holders:
        for permission in holder.permissions:
            _collect_endpoint_leaves(permission, set(), allowed)
    # de-duplicate while preserving a stable order
    unique: list[Permission] = []
    for permission in allowed:
        if permission.id not in seen:
            seen.add(permission.id)
            unique.append(permission)
    return unique


def check_permission_tree(permission_holder: User | Group, permission: Permission) -> bool:
    visited = set()
    while permission is not None:
        if permission.id in visited:
            print(f"Permission checking cycle detected after {len(visited)} visited nodes")
            return False
        visited.add(permission.id)
        if permission in permission_holder.permissions:
            return True
        else:
            permission = permission.parentPermission
    return False


def check_permission(db: Session, user: User, permission: Permission) -> bool:
    return (check_permission_tree(permission_holder=user, permission=permission) 
            or any([check_permission_tree(permission_holder=group, permission=permission) for group in user.groups]))


def user_holds_endpoint(db: Session, user: User, method: str, route: str) -> bool:
    """Whether `user` may perform one specific endpoint action.

    The same decision ``check_permissions`` makes for the currently-requested
    route, but for an arbitrary user (e.g. one supplied via body credentials):
    the user directly holds the endpoint permission, one of the user's groups
    holds it, or they (a group) hold a more general scope of which the
    endpoint is a descendant (e.g. the global root permission).
    """
    permission = get_permission_by_route_and_method(db=db, route=route, method=method)
    if permission is None:
        return False
    return check_permission(db=db, user=user, permission=permission)


def user_has_scope(db: Session, user: User, scope_route: str) -> bool:
    """Whether `user` can act anywhere within `scope_route`, directly or via a
    group — including through a more general scope covering it (e.g. the
    global root), whose endpoint leaves all fall under the scope.
    """
    for holder in [user, *user.groups]:
        leaves: list[Permission] = []
        for granted in holder.permissions:
            _collect_endpoint_leaves(granted, set(), leaves)
        if any(leaf.route == scope_route or leaf.route.startswith(scope_route + "/") for leaf in leaves):
            return True
    return False