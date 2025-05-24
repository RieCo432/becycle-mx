import os
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


users = APIRouter(
    tags=["users"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@users.get("/users/me")
async def get_user_me(
        current_user: Annotated[models.User, Depends(dep.get_current_active_user)]
) -> schemas.User:
    return current_user


@users.get("/users")
async def get_users(db: Session = Depends(dep.get_db)) -> list[schemas.User]:
    return crud.get_users(db=db)


@users.post("/users")
async def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(dep.get_db),
) -> schemas.User:
    created_user = crud.create_user(user_data=user_data, db=db)
    return created_user


@users.post("/users/check/password")
async def post_user_password_check(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)
) -> bool:
    user = crud.authenticate_user(db=db, username=form_data.username, password_cleartext=form_data.password)

    return user is not None


@users.post("/users/check/password-or-pin")
async def post_user_password_or_pin_check(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)
) -> bool:
    user = crud.validate_user_signature(db=db, username=form_data.username, password_or_pin=form_data.password)

    return user is not None


@users.get("/users/active-users")
async def get_active_users(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    active_users = crud.get_active_users(db=db)
    return active_users


@users.get("/users/deposit-bearers")
async def get_deposit_bearers(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    deposit_bearers = crud.get_deposit_bearers(db=db)
    return deposit_bearers


@users.get("/users/rental-checkers")
async def get_rental_checkers(
        db: Session = Depends(dep.get_db)
) -> list[schemas.User]:
    rental_checkers = crud.get_rental_checkers(db=db)
    return rental_checkers


@users.post("/users/presentation-card/{presentation_card_id}")
async def update_presentation_card(
        presentation_card_id: UUID,
        name: Annotated[str, Body(embed=True)],
        bio: Annotated[str, Body(embed=True)],
        photo: UploadFile | None = None,
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    presentation_card = crud.get_user_presentation_card_by_id(db=db, presentation_card_id=presentation_card_id)
    return crud.update_or_create_user_presentation_card(db=db, user=presentation_card.user, name=name, bio=bio, photo=photo)


@users.delete("/users/presentation-card/{presentation_card_id}")
async def delete_presentation_card(
        presentation_card_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    return crud.delete_user_presentation_card_by_id(db=db, presentation_card_id=presentation_card_id)


@users.post("/users/me/presentation-card")
async def update_my_presentation_card(
        name: Annotated[str, Body(embed=True)],
        bio: Annotated[str, Body(embed=True)],
        photo: UploadFile | None = None,
        user: models.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    return crud.update_or_create_user_presentation_card(db=db, user=user, name=name, bio=bio, photo=photo)


@users.get("/users/me/presentation-card")
async def get_my_presentation_card(
        user: models.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    return crud.get_user_presentation_card(db=db, user=user)


@users.delete("/users/me/presentation-card")
async def delete_my_presentation_card(
        user: models.User = Depends(dep.get_current_active_user),
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    return crud.delete_user_presentation_card(db=db, user=user)

@users.get("/users/me/groups")
async def get_user_groups(
        user: models.User = Depends(dep.get_current_active_user),
) -> list[schemas.Group]:
    return user.groups


@users.get("/users/{user_id}")
async def get_user(user_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.User:
    return crud.get_user(db=db, user_id=user_id)


@users.patch("/users/{user_id}")
async def patch_user(user_id: UUID,
                     updated_user_data: schemas.UserUpdate,
                     current_user: models.User = Depends(dep.get_current_active_user),
                     db: Session = Depends(dep.get_db)) -> schemas.User:
    if current_user.id == user_id and updated_user_data.roles_change():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "You cannot modify your own roles!"})
    user = crud.get_user(db=db, user_id=user_id)
    if user.softDeleted and updated_user_data.softDeleted is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User is soft-deleted"})
    return crud.update_user(db=db,
                            user=user,
                            updated_user_data=updated_user_data)


@users.post("/users/{user_id}/permissions")
async def grant_user_permission(user_id: UUID, permission: schemas.NewUserPermission, db: Session = Depends(dep.get_db)) -> schemas.UserPermission:
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    elif user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User is soft-deleted"})
    permission = crud.get_permission(db=db, permission_id=permission.permissionId)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})
    if permission in user.permissions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User already has permission"})

    return crud.add_user_permission(db=db, user_id=user_id, permission_id=permission.id)


@users.delete("/users/{user_id}/permissions/{permission_scope_id}")
async def revoke_user_permission(user_id: UUID, permission_scope_id: UUID, db: Session = Depends(dep.get_db)) -> list[UUID]:
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    elif user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User is soft-deleted"})
    if crud.get_permission(db=db, permission_id=permission_scope_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Permission scope not found"})

    return crud.delete_user_permission(db=db, user_id=user_id, permission_scope_id=permission_scope_id)

@users.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: UUID, db: Session = Depends(dep.get_db)) -> list[schemas.Permission]:
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    elif user.softDeleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "User is soft-deleted"})
    return user.permissions


@users.get("/users/{user_id}/presentation-card")
async def get_user_presentation_card(
        user_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.UserPresentationCard:
    user = crud.get_user(db=db, user_id=user_id)
    return crud.get_user_presentation_card(db=db, user=user)

@users.get("/users/{user_id}/groups")
async def get_user_groups(
        user_id: UUID,
        db: Session = Depends(dep.get_db)
) -> list[schemas.Group]:
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "User not found"})
    return user.groups
