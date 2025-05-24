from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app import auth
from app.models import Group


groups = APIRouter(
    tags=["groups"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@groups.get("/groups")
async def get_groups(db: Session = Depends(dep.get_db)) -> list[schemas.Group]:
    return crud.get_groups(db=db)


@groups.post("/groups")
async def create_new_group(group_data: schemas.GroupCreate, db: Session = Depends(dep.get_db)) -> schemas.Group:
    return crud.create_group(db=db, group_name=group_data.name)


@groups.delete("/groups/{group_id}")
async def delete_group(group_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Group:
    return crud.delete_group(db=db, group_id=group_id)


@groups.get("/groups/{group_id}/users")
async def get_group_users(group_id: UUID, db: Session = Depends(dep.get_db)) -> list[schemas.User]:
    group = crud.get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    return group.users


@groups.post("/groups/{group_id}/users")
async def add_user_to_group(
        group_id: UUID,
        user_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.GroupUser:
    return crud.add_user_to_group(db=db, user_id=user_id, group_id=group_id)


@groups.delete("/groups/{group_id}/users/{user_id}")
async def remove_user_from_group(
        user_id: UUID,
        group_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.User:
    return crud.remove_user_from_group(db=db, user_id=user_id, group_id=group_id)


@groups.get("/groups/{group_id}/permissions")
async def get_group_permissions(group_id: UUID, db: Session = Depends(dep.get_db)) -> list[schemas.Permission]:
    group = crud.get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    return group.permissions


@groups.post("/groups/{group_id}/permissions")
async def add_permission_to_group(
        group_id: UUID,
        permission: schemas.NewUserPermission,
        db: Session = Depends(dep.get_db)
) -> schemas.GroupPermission:
    return crud.add_permission_to_group(db=db, group_id=group_id, permission_id=permission.permissionId)


@groups.delete("/groups/{group_id}/permissions/{permission_scope_id}")
async def remove_permission_from_group(
        group_id: UUID,
        permission_scope_id: UUID,
        db: Session = Depends(dep.get_db)
) -> list[UUID]:
    return crud.remove_permission_from_group(db=db, group_id=group_id, permission_id=permission_scope_id)
