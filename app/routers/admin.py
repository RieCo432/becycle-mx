from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated


# TODO: PUT ADMIN AS DEPENDENCY
admin = APIRouter(
    tags=["admin"],
    responses={404: {"description": "Not Found"}})


@admin.get("/admin/duplicates/clients")
async def admin_duplicates_clients(db: Session = Depends(dep.get_db)) -> list[schemas.DetectedPotentialClientDuplicates]:
    return crud.get_potential_client_duplicates_detected(db=db)


@admin.get("/admin/duplicates/clients/refresh")
async def admin_duplicates_clients_refresh(
        refresh_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> None:
    refresh_tasks.add_task(crud.find_potential_client_duplicates, db)


@admin.put("/admin/duplicates/clients/resolve/{potential_client_duplicate_id}")
async def admin_duplicates_client_resolve(
        potential_client_duplicate_id: UUID,
        discard_client_id: Annotated[UUID, Body(embed=True)],
        keep_client_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)) -> None:
    if keep_client_id == discard_client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Both IDs are identical"})
    crud.resolve_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id, discard_client_id=discard_client_id, keep_client_id=keep_client_id)


@admin.patch("/admin/duplicates/clients/ignore/{potential_client_duplicate_id}")
async def admin_duplicates_client_ignore(
        potential_client_duplicate_id: UUID,
        db: Session = Depends(dep.get_db)) -> None:
    crud.ignore_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)
