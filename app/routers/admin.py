from uuid import UUID
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from typing import Annotated


admin = APIRouter(
    tags=["admin"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.get_current_admin_user)]
)


@admin.get("/admin/duplicates/clients")
async def get_admin_duplicates_clients(db: Session = Depends(dep.get_db)) -> list[schemas.DetectedPotentialClientDuplicates]:
    return crud.get_potential_client_duplicates_detected(db=db)


@admin.get("/admin/duplicates/clients/refresh")
async def admin_duplicates_clients_refresh(
        refresh_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> None:
    refresh_tasks.add_task(crud.find_potential_client_duplicates, db)


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
        refresh_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> None:
    refresh_tasks.add_task(crud.find_potential_bike_duplicates, db)


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
