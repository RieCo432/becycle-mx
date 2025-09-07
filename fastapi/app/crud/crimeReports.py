import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from sqlalchemy import select, func


def get_crime_report(crime_report_id: UUID, db: Session) -> models.CrimeReport:
    return db.scalar(
        select(models.CrimeReport)
        .where(models.CrimeReport.id == crime_report_id)
    )


def get_crime_reports(db: Session, crime_report_id: UUID | None = None, crime_number: str | None = None, contract_id: UUID | None = None) -> List[models.CrimeReport]:
    query = select(models.CrimeReport)

    if crime_report_id is not None:
        query = query.where(models.CrimeReport.id == crime_report_id)

    if crime_number is not None:
        query = query.where(models.CrimeReport.crimeNumber == crime_number.lower().replace(" ", "").replace("-", ""))

    if contract_id is not None:
        query = query.where(models.CrimeReport.contractId == contract_id)

    return [_ for _ in db.scalars(query)]


def create_crime_report(crime_report_data: schemas.CrimeReport, db: Session) -> models.CrimeReport:
    crime_report = models.CrimeReport(
        contractId=crime_report_data.contractId,
        createdOn=datetime.datetime.utcnow(),
        crimeNumber=crime_report_data.crimeNumber.lower().replace(" ", "").replace("-", "")
    )
    db.add(crime_report)
    db.commit()
    return crime_report


def close_crime_report(crime_report_id: UUID, db: Session) -> models.CrimeReport:
    crime_report = get_crime_report(crime_report_id=crime_report_id, db=db)
    crime_report.closedOn = datetime.datetime.utcnow()
    db.commit()
    return crime_report


def find_crime_reports(db: Session, crime_number: str, max_distance: int = 4) -> List[models.CrimeReport]:
    return [_ for _ in db.scalars(
        select(models.CrimeReport)
        .where(
            (models.CrimeReport.crimeNumber.contains(crime_number))
            | (func.levenshtein(models.CrimeReport.crimeNumber, crime_number) <= max_distance)
        )
    )]