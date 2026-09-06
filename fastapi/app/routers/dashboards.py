from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from fastapi.params import Query
from sqlalchemy.orm import Session

import app.dependencies as dep
from app import models, schemas, crud
from typing import List, Annotated

dashboards = APIRouter(
    tags=["dashbaords"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(dep.check_permissions)]
)


@dashboards.get("/dashboards")
async def get_dashboards(
        db: Session = Depends(dep.get_db)
) -> list[schemas.Dashboard]:
    return crud.get_dashboards(db=db)

@dashboards.post("/dashboards")
async def create_dashboard(
        new_dashboard_data: schemas.DashboardCreate, 
        db: Session = Depends(dep.get_db)) -> schemas.Dashboard:
    return crud.create_dashboard(db=db, new_dashboard_data=new_dashboard_data)


@dashboards.put("/dashboards/{dashboards_id}")
async def update_dashboard(
        dashboards_id: UUID,
        updated_dashboard_data: schemas.DashboardCreate, 
        db: Session = Depends(dep.get_db)) -> schemas.Dashboard:
    return crud.update_dashboard(db=db, dashboards_id=dashboards_id, updated_dashboard_data=updated_dashboard_data)


@dashboards.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
        dashboard_id: UUID,
        db: Session = Depends(dep.get_db)) -> None:
    crud.delete_dashboard(db=db, dashboard_id=dashboard_id)
    
    
@dashboards.patch("/dashboards/{dashboard_id}/up")
async def move_dashboard_up(
        dashboard_id: UUID,
        db: Session = Depends(dep.get_db)) -> None:
    crud.move_dashboard_up(db=db, dashboard_id=dashboard_id)
    
    
@dashboards.patch("/dashboards/{dashboard_id}/down")
async def move_dashboard_down(
        dashboard_id: UUID,
        db: Session = Depends(dep.get_db)) -> None:
    crud.move_dashboard_down(db=db, dashboard_id=dashboard_id)
    
