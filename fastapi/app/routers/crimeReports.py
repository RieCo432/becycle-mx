from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

crime_reports = APIRouter(
    tags=["crimereports"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@crime_reports.get("/crimereports")
async def get_crime_reports(
        id: UUID | None = None,
        crime_number: str | None = None,
        contract_id: UUID | None = None,
        db: Session = Depends(dep.get_db)
) -> List[schemas.CrimeReport]:
    return crud.get_crime_reports(db=db, crime_report_id=id, crime_number=crime_number, contract_id=contract_id)


@crime_reports.post("/crimereports")
async def create_crime_report(
        crime_report_data: schemas.CrimeReportCreate,
        db: Session = Depends(dep.get_db)
) -> schemas.CrimeReport:
    contract = crud.get_contract(db=db, contract_id=crime_report_data.contractId)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Contract not found"})
    if contract.returnedDate is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Contract is already returned"})
    existing_crime_reports = crud.get_crime_reports(db=db, contract_id=crime_report_data.contractId)
    if len([report for report in existing_crime_reports if report.closedOn is None]) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "There is already an open crime report for this contract!"})
    return crud.create_crime_report(crime_report_data=crime_report_data, db=db)


@crime_reports.patch("/crimereports/{crime_report_id}/close")
async def close_crime_report(
        crime_report_id: UUID,
        db: Session = Depends(dep.get_db)
) -> schemas.CrimeReport:
    crime_report = crud.get_crime_report(crime_report_id, db)
    if crime_report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Crime Report not found"})
    return crud.close_crime_report(crime_report_id=crime_report.id, db=db)
