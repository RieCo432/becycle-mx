from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app.services.misc_helpers import run_in_new_session

admin = APIRouter(
    tags=["admin"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.check_permissions)]
)


@admin.get("/admin/duplicates/clients")
async def get_admin_duplicates_clients(db: Session = Depends(dep.get_db)) -> list[schemas.DetectedPotentialClientDuplicates]:
    return crud.get_potential_client_duplicates_detected(db=db)


@admin.get("/admin/duplicates/clients/refresh")
async def admin_duplicates_clients_refresh(
        refresh_tasks: BackgroundTasks) -> None:
    refresh_tasks.add_task(run_in_new_session, crud.find_potential_client_duplicates)


@admin.put("/admin/duplicates/clients/{potential_client_duplicate_id}/resolve")
async def admin_duplicates_client_resolve(
        potential_client_duplicate_id: UUID,
        discard_client_id: Annotated[UUID, Body(embed=True)],
        keep_client_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)) -> None:
    if keep_client_id == discard_client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Both IDs are identical"})
    crud.resolve_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id, discard_client_id=discard_client_id, keep_client_id=keep_client_id)


@admin.patch("/admin/duplicates/clients/{potential_client_duplicate_id}/ignore")
async def admin_duplicates_client_ignore(
        potential_client_duplicate_id: UUID,
        db: Session = Depends(dep.get_db)) -> schemas.DetectedPotentialClientDuplicates:
    return crud.ignore_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)


@admin.get("/admin/duplicates/bikes")
async def get_admin_duplicates_bikes(db: Session = Depends(dep.get_db)) -> list[schemas.DetectedPotentialBikeDuplicates]:
    return crud.get_potential_bike_duplicates_detected(db=db)


@admin.get("/admin/duplicates/bikes/refresh")
async def admin_duplicates_bikes_refresh(
        refresh_tasks: BackgroundTasks) -> None:
    refresh_tasks.add_task(run_in_new_session, crud.find_potential_bike_duplicates)


@admin.put("/admin/duplicates/bikes/{potential_bike_duplicate_id}/resolve")
async def admin_duplicates_bike_resolve(
        potential_bike_duplicate_id: UUID,
        discard_bike_id: Annotated[UUID, Body(embed=True)],
        keep_bike_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)) -> None:
    if keep_bike_id == discard_bike_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Both IDs are identical"})
    crud.resolve_bike_duplicate(db=db, potential_bike_duplicate_id=potential_bike_duplicate_id, discard_bike_id=discard_bike_id, keep_bike_id=keep_bike_id)


@admin.patch("/admin/duplicates/bikes/{potential_bike_duplicate_id}/ignore")
async def admin_duplicates_client_ignore(
        potential_bike_duplicate_id: UUID,
        db: Session = Depends(dep.get_db)) -> schemas.DetectedPotentialBikeDuplicates:
    return crud.ignore_potential_bike_duplicate(db=db, potential_bike_duplicate_id=potential_bike_duplicate_id)


@admin.get("/admin/takeout/contracts.xlsx")
async def get_contracts_takeout_excel(db: Session = Depends(dep.get_db)):
    return FileResponse(crud.get_contracts_takeout_excel(db=db))


@admin.get("/admin/takeout/contracts.pdf")
async def get_contracts_takeout_pdf(db: Session = Depends(dep.get_db)):
    return FileResponse(crud.get_contracts_takeout_pdf(db=db))


@admin.get("/admin/permissions")
async def get_permissions(db: Session = Depends(dep.get_db)) -> schemas.PermissionNode:
    result = crud.get_permissions_tree(db=db)
    return result


# #510 A-2..A-5: the AI audit trail — all client-route AI replies, newest
# first, each with its detected intent and the prompting context. Admin-only:
# this router enforces check_permissions, the permission row for the route is
# created by the startup sync, and only the admin group holds a scope
# covering it (regular staff groups hold narrower scopes).
@admin.get("/admin/ai-replies")
async def get_ai_replies(
        search: Annotated[str | None, Query()] = None,
        rating: Annotated[str | None, Query()] = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 50,
        db: Session = Depends(dep.get_db)) -> list[schemas.AiAuditEntry]:
    # `search` (#510 A-6): case-insensitive match on the reply body, intent,
    # the shown context, or the client's name/email.
    # `rating` (#510 A-8): 'good' | 'not-good' | 'unrated', or all when absent.
    # `limit`: batch size, newest first (the admin view loads the last 50).
    if rating is not None and rating not in crud.QUALITY_RATINGS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"description": "rating must be 'good', 'not-good' or 'unrated'"})
    return crud.get_client_route_ai_replies(db=db, search=search, rating=rating, limit=limit)


# #510 A-8: set or clear the quality rating on an AI reply. A dedicated
# route, guarded by the existing permission system like the rest of this
# router (the startup sync creates its permission row; only the admin group
# holds a scope covering it).
@admin.post("/admin/ai-replies/{message_id}/rating")
async def rate_ai_reply(
        message_id: UUID,
        update: schemas.QualityRatingUpdate,
        db: Session = Depends(dep.get_db)) -> schemas.QualityRatingState:
    if update.rating not in crud.QUALITY_RATINGS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"description": "rating must be 'good', 'not-good' or 'unrated'"})
    if not crud.set_message_quality_rating(db=db, message_id=message_id, rating=update.rating):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"description": "Message not found"})
    return schemas.QualityRatingState(qualityRating=crud.QUALITY_RATINGS[update.rating])
