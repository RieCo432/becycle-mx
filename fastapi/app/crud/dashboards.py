from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, Integer
from sqlalchemy.orm import Session
from starlette import status

import app.models as models
import app.schemas as schemas


def get_dashboard(db: Session, dashboard_id: UUID) -> models.Dashboard:
    dashboard = db.scalar(
        select(models.Dashboard)
        .where(models.Dashboard.id == dashboard_id)
    )
    
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Dashboard not found"})
    return dashboard


def get_dashboards(db: Session) -> list[schemas.Dashboard]:
    dashboards = [_ for _ in db.scalars(select(models.Dashboard))]
    return dashboards


def create_dashboard(db: Session, new_dashboard_data: schemas.DashboardCreate) -> schemas.Dashboard:
    highest_index = get_highest_index(db)
    new_dashboard = models.Dashboard(**new_dashboard_data.model_dump())
    new_dashboard.index = highest_index + 1
    db.add(new_dashboard)
    db.commit()
    db.refresh(new_dashboard)
    
    enumerate_all_dashboards(db=db)
    
    return new_dashboard


def get_highest_index(db: Session) -> int:
    highest_index = db.scalar(select(func.cast(func.max(models.Dashboard.index), Integer)))
    assert isinstance(highest_index, int | None)
    highest_index = highest_index if highest_index is not None else -1
    return highest_index


def update_dashboard(db: Session, dashboards_id: UUID, updated_dashboard_data: schemas.DashboardCreate) -> schemas.Dashboard:
    dashboard = get_dashboard(db=db, dashboard_id=dashboards_id)
    dashboard.name = updated_dashboard_data.name
    dashboard.layout = updated_dashboard_data.layout
    db.commit()
    db.refresh(dashboard)

    enumerate_all_dashboards(db=db)
    
    return dashboard


def delete_dashboard(db: Session, dashboard_id: UUID) -> None:
    dashboard = get_dashboard(db=db, dashboard_id=dashboard_id)
    db.delete(dashboard)
    db.commit()

    enumerate_all_dashboards(db=db)
    
    
def move_dashboard_up(db: Session, dashboard_id: UUID) -> None:
    dashboard = get_dashboard(db=db, dashboard_id=dashboard_id)
    
    if dashboard.index == 0:
        raise HTTPException(status_code=400, detail={"description": "Dashboard is already at the top"})
    
    dashboard_above = db.scalar(
        select(models.Dashboard)
        .where(models.Dashboard.index < dashboard.index)
        .order_by(models.Dashboard.index.desc())
        .limit(1)
    )
    
    if dashboard_above is None:
        raise HTTPException(status_code=400, detail={"description": "Dashboard is already at the top"})
    
    upper_index = dashboard_above.index
    lower_index = dashboard.index
    
    dashboard_above.index = -1
    db.commit()
    
    dashboard.index = upper_index
    db.commit()
    
    dashboard_above.index = lower_index
    db.commit()

    enumerate_all_dashboards(db=db)
    
    
def move_dashboard_down(db: Session, dashboard_id: UUID) -> None:
    dashboard = get_dashboard(db=db, dashboard_id=dashboard_id)
    
    highest_index = get_highest_index(db=db)
    
    if dashboard.index == highest_index:
        raise HTTPException(status_code=400, detail={"description": "Dashboard is already at the bottom"})
    
    
    dashboard_below = db.scalar(
        select(models.Dashboard)
        .where(models.Dashboard.index > dashboard.index)
        .order_by(models.Dashboard.index)
        .limit(1)
    )
    
    if dashboard_below is None:
        raise HTTPException(status_code=400, detail={"description": "Dashboard is already at the bottom"})

    upper_index = dashboard.index
    lower_index = dashboard_below.index

    dashboard_below.index = -1
    db.commit()
    
    dashboard.index = lower_index
    db.commit()
    
    dashboard_below.index = upper_index
    db.commit()

    enumerate_all_dashboards(db=db)
    
    
def enumerate_all_dashboards(db: Session) -> None:
    # This ensures the range of indices goes from 0 to the number of dashboards -1, with no gaps 
    dashboards_in_order = [_ for _ in db.scalars(select(models.Dashboard).order_by(models.Dashboard.index))]
    
    for dashboard in dashboards_in_order:
        dashboard.index = -dashboard.index
        
    db.commit()
    
    for index, dashboard in enumerate(dashboards_in_order):
        dashboard.index = index

    db.commit()