import os
from datetime import timedelta
from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas
from app import auth
from app.models import Group


groups = APIRouter(
    tags=["groups"],
    responses={404: {"description": "Not Found"}}
)


@groups.get("/groups", dependencies=[Depends(dep.get_current_active_user)])
async def get_groups(db: Session = Depends(dep.get_db)) -> list[schemas.Group]:
    return crud.get_groups(db=db)


@groups.post("/groups", dependencies=[Depends(dep.get_current_admin_user)])
async def create_new_group(group_data: schemas.GroupCreate, db: Session = Depends(dep.get_db)) -> schemas.Group:
    return crud.create_group(db=db, group_name=group_data.name)


@groups.delete("/groups/{group_id}", dependencies=[Depends(dep.get_current_admin_user)])
async def delete_group(group_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.Group:
    return crud.delete_group(db=db, group_id=group_id)


@groups.get("/groups/{group_id}/users", dependencies=[Depends(dep.get_current_active_user)])
async def get_group_users(group_id: UUID, db: Session = Depends(dep.get_db)) -> list[schemas.User]:
    group = crud.get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    return group.users


@groups.post("/groups/{group_id}/users", dependencies=[Depends(dep.get_current_admin_user)])
async def add_user_to_group(
        group_id: UUID,
        user_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.GroupUser:
    return crud.add_user_to_group(db=db, user_id=user_id, group_id=group_id)


@groups.delete("/groups/{group_id}/users/{user_id}", dependencies=[Depends(dep.get_current_admin_user)])
async def remove_user_from_group(
        user_id: UUID,
        group_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.User:
    return crud.remove_user_from_group(db=db, user_id=user_id, group_id=group_id)


@groups.get("/groups/{group_id}/permissions", dependencies=[Depends(dep.get_current_active_user)])
async def get_group_permissions(group_id: UUID, db: Session = Depends(dep.get_db)) -> list[schemas.Permission]:
    group = crud.get_group(db=db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Group not found"})
    return group.permissions


@groups.post("/groups/{group_id}/permissions", dependencies=[Depends(dep.get_current_admin_user)])
async def add_permission_to_group(
        group_id: UUID,
        permission_scope_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.GroupPermission:
    return crud.add_permission_to_group(db=db, group_id=group_id, permission_scope_id=permission_scope_id)


@groups.delete("/groups/{group_id}/permissions/{permission_scope_id}", dependencies=[Depends(dep.get_current_admin_user)])
async def remove_permission_from_group(
        group_id: UUID,
        permission_scope_id: UUID,
        db: Session = Depends(dep.get_db)
) -> list[UUID]:
    return crud.remove_permission_from_group(db=db, group_id=group_id, permission_scope_id=permission_scope_id)
