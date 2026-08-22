import os
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])

bug_reports = APIRouter(
    tags=["bugreports"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@bug_reports.get("/bugreports")
async def get_bug_reports(db: Session = Depends(dep.get_db)) -> list[schemas.BugReport]:
    return crud.get_bug_reports(db=db)


@bug_reports.get("/bugreports/{bug_report_id}")
async def get_bug_report(bug_report_id: UUID, db: Session = Depends(dep.get_db)) -> schemas.BugReport | None:
    return crud.get_bug_report(db=db, bug_report_id=bug_report_id)


@bug_reports.post("/bugreports")
async def create_bug_report(bug_report_data: schemas.BugReportCreate,
                            current_user: models.User = Depends(dep.get_current_active_user),
                            db: Session = Depends(dep.get_db)) -> schemas.BugReport:
    return crud.create_bug_report(db=db, user=current_user, bug_report_data=bug_report_data)


@bug_reports.patch("/bugreports/{bug_report_id}")
async def patch_bug_report(bug_report_id: UUID,
                           bug_report_update_data: schemas.BugReportUpdate,
                           db: Session = Depends(dep.get_db)) -> schemas.BugReport:
    return crud.update_bug_report(db=db, bug_report_id=bug_report_id, bug_report_update_data=bug_report_update_data)


@bug_reports.delete("/bugreports/{bug_report_id}")
async def delete_bug_report(bug_report_id: UUID,
                            db: Session = Depends(dep.get_db)) -> None:
    crud.delete_bug_report(db=db, bug_report_id=bug_report_id)


@bug_reports.post("/bugreports/merge")
async def merge_bug_reports(ids: list[UUID] = Query(min_length=2),
                            db: Session = Depends(dep.get_db)) -> schemas.BugReport:
    return crud.merge_bug_reports(db=db, bug_report_ids=ids)
