import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_bug_reports(db: Session, bug_report_ids: list[UUID] = None) -> list[models.BugReport]:
    if bug_report_ids is not None:
        return [_ for _ in db.scalars(
            select(models.BugReport)
            .join(models.User)
            .where(models.BugReport.id.in_(bug_report_ids))
        )]
    return [_ for _ in db.scalars(
        select(models.BugReport)
        .join(models.User)
    )]


def get_bug_report(db: Session, bug_report_id: UUID) -> models.BugReport | None:
    return db.scalar(
        select(models.BugReport)
        .join(models.User)
        .where(models.BugReport.id == bug_report_id)
    )


def create_bug_report(db: Session, user: models.User, bug_report_data: schemas.BugReportCreate) -> models.BugReport:
    bug_report = models.BugReport(
        reportedByUserId=user.id,
        pageAddress=bug_report_data.pageAddress,
        description=bug_report_data.description,
        consoleHistory=bug_report_data.consoleHistory
    )
    try:
        db.add(bug_report)
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Integrity Error: Does this bug report already exist?"}
        )
    return bug_report


def update_bug_report(db: Session,
                      bug_report_id: UUID,
                      bug_report_update_data: schemas.BugReportUpdate) -> models.BugReport:
    bug_report = get_bug_report(db, bug_report_id)
    if bug_report is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"description": "Bug report not found. It may have been deleted"})

    bug_report.description = bug_report_update_data.description

    db.commit()

    return bug_report


def delete_bug_report(db: Session, bug_report_id: UUID) -> None:
    bug_report = get_bug_report(db, bug_report_id)
    if bug_report is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"description": "Bug report not found. It may have already been deleted"})

    db.delete(bug_report)
    db.commit()


def merge_bug_reports(db: Session, bug_report_ids: list[UUID]) -> models.BugReport:
    bug_reports = get_bug_reports(db, bug_report_ids)
    if len(bug_reports) != len(bug_report_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"description": "Couldn't find the bug reports to merge"})
    merge_bug_report = bug_reports[0]

    merge_console_history = json.loads(merge_bug_report.consoleHistory)

    for bug_report in bug_reports[1:]:
        if (merge_bug_report.pageAddress != bug_report.pageAddress
                and len(f"{merge_bug_report.pageAddress} | {bug_report.pageAddress}") <= 255):
            merge_bug_report.pageAddress += f" | {bug_report.pageAddress}"
        if (merge_bug_report.description != bug_report.description
                and len(f"{merge_bug_report.description}\n{bug_report.description}") <= 1024):
            merge_bug_report.description += f"\n{bug_report.description}"
        merge_console_history.extend(json.loads(merge_bug_report.consoleHistory))
        db.delete(bug_report)

    merge_bug_report.consoleHistory = json.dumps(merge_console_history)
    db.commit()

    return merge_bug_report
