import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

import app.models as models
import app.schemas as schemas


def get_dashboard(db: Session, dashboards_id: UUID) -> models.Dashboard:
    dashboard = db.scalar(
        select(models.Dashboard)
        .where(models.Dashboard.id == dashboards_id)
    )
    
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Dashboard not found"})
    return dashboard


def get_dashboards(db: Session) -> list[schemas.Dashboard]:
    dashboards = [_ for _ in db.scalars(select(models.Dashboard))]
    return dashboards


def create_dashboard(db: Session, new_dashboard_data: schemas.DashboardCreate) -> schemas.Dashboard:
    new_dashboard = models.Dashboard(**new_dashboard_data.model_dump())
    db.add(new_dashboard)
    db.commit()
    db.refresh(new_dashboard)
    return new_dashboard


def update_dashboard(db: Session, dashboards_id: UUID, updated_dashboard_data: schemas.DashboardCreate) -> schemas.Dashboard:
    dashboard = get_dashboard(db=db, dashboards_id=dashboards_id)
    dashboard.name = updated_dashboard_data.name
    dashboard.layout = updated_dashboard_data.layout
    db.commit()
    db.refresh(dashboard)
    return dashboard