from datetime import date, time
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas

settings = APIRouter(
    tags=["settings"],
    dependencies=[Depends(dep.get_db), Depends(dep.check_permissions)],
    responses={404: {"description": "Not Found"}}
)


@settings.get("/settings/appointments/general")
async def get_appointment_general_settings(
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentGeneralSettings:

    return crud.get_appointment_general_settings(db=db)


@settings.patch("/settings/appointments/general")
async def update_appointment_general_settings(
        updated_appointment_settings: schemas.PatchAppointmentGeneralSettings,
        db: Session = Depends(dep.get_db)
) -> schemas.AppointmentGeneralSettings:
    return crud.update_appointment_general_settings(db=db, updated_appointment_settings=updated_appointment_settings)


@settings.get("/settings/appointments/concurrency")
async def get_appointment_concurrency_limits(
        db: Session = Depends(dep.get_db)) -> list[schemas.AppointmentConcurrencyLimit]:

    return crud.get_appointment_concurrency_limits(db=db)


@settings.post("/settings/appointments/concurrency")
async def create_appointment_concurrency_limit(
        appointment_concurrency_limit_data: schemas.AppointmentConcurrencyLimit,
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentConcurrencyLimit:

    return crud.add_appointment_concurrency_limit(
        db=db,
        appointment_concurrency_limit_data=appointment_concurrency_limit_data)


@settings.delete("/settings/appointments/concurrency/{weekday}/{after_time}")
async def delete_appointment_concurrency_limit(
        weekday: int,
        after_time: time,
        db: Session = Depends(dep.get_db)) -> None:
    crud.delete_appointment_concurrency_limit(db=db, weekday=weekday, after_time=after_time)



@settings.patch("/settings/appointments/concurrency/{weekday}/{after_time}")
async def update_appointment_concurrency_limit(
        weekday: int,
        after_time: time,
        new_appointment_concurrency_limit_data: schemas.PatchAppointmentConcurrencyLimit,
        db: Session = Depends(dep.get_db)) -> schemas.AppointmentConcurrencyLimit:
    return crud.patch_appointment_concurrency_limit(db=db, weekday=weekday, after_time=after_time, new_appointment_concurrency_limit_data=new_appointment_concurrency_limit_data)


@settings.get("/settings/closed-days")
async def get_closed_days(start_date: date | None = None, end_date: date | None = None, db: Session = Depends(dep.get_db)) -> list[schemas.ClosedDay]:
    return crud.get_closed_days(db=db, start_date=start_date, end_date=end_date)


@settings.post("/settings/closed-day")
async def create_closed_day(
        closed_day_data: schemas.ClosedDay,
        db: Session = Depends(dep.get_db)) -> schemas.ClosedDay:

    return crud.create_closed_day(db=db, closed_day_data=closed_day_data)


@settings.delete("/settings/closed-day/{closed_day_date}")
async def delete_closed_day(
        closed_day_date: date,
        db: Session = Depends(dep.get_db)):

    crud.delete_closed_day(db=db, closed_day_date=closed_day_date)


@settings.put("/settings/address")
async def update_address(new_address: schemas.Address, db: Session = Depends(dep.get_db)) -> schemas.Address:
    return crud.update_address(db=db, new_address=new_address)


@settings.post("/settings/contract-types")
async def add_contract_type(
        new_contract_type: schemas.ContractType,
        db: Session = Depends(dep.get_db)
) -> schemas.ContractType:
    return crud.add_contract_type(db=db, new_contract_type=new_contract_type)


@settings.delete("/settings/contract-types/{contract_type_id}")
async def delete_contract_type(
        contract_type_id: str,
        db: Session = Depends(dep.get_db)
) -> schemas.ContractType:
    return crud.delete_contract_type(db=db, contract_type_id=contract_type_id)


@settings.post("/settings/expense-types")
async def add_expense_type(
        new_expense_type: schemas.ExpenseType,
        db: Session = Depends(dep.get_db)
) -> schemas.ExpenseType:
    return crud.add_expense_type(db=db, new_expense_type=new_expense_type)


@settings.delete("/settings/expense-types/{expense_type_id}")
async def delete_expense_type(
        expense_type_id: str,
        db: Session = Depends(dep.get_db)
) -> schemas.ExpenseType:
    return crud.delete_expense_type(db=db, expense_type_id=expense_type_id)


@settings.patch("/settings/expense-types/{expense_type_id}")
async def update_expense_type(
        expense_type_id: str,
        description: Annotated[str, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> schemas.ExpenseType:
    return crud.update_expense_type(db=db, expense_type_id=expense_type_id, description=description)


@settings.patch("/settings/about-us")
async def update_about_us(
        new_about_us: schemas.AboutUs,
        db: Session = Depends(dep.get_db)
) -> schemas.AboutUs:
    return crud.set_about_us_html(db=db, new_about_us= new_about_us)


@settings.get("/settings/faq")
async def get_all_faq(db: Session = Depends(dep.get_db)) -> list[schemas.Faq]:
    return crud.get_all_faq(db=db)


@settings.post("/settings/faq")
async def post_faq(
        new_faq: schemas.FaqBase,
        db: Session = Depends(dep.get_db)
) -> schemas.Faq:
    return crud.create_faq(db=db, new_faq=new_faq)

@settings.patch("/settings/faq/swap")
async def patch_swap_faq(
        faq1_id: Annotated[UUID, Body(embed=True)],
        faq2_id: Annotated[UUID, Body(embed=True)],
        db: Session = Depends(dep.get_db)
) -> list[schemas.Faq]:
    if crud.get_faq(db=db, faq_id=faq1_id) is None or crud.get_faq(db=db, faq_id=faq2_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more FAQ not found."})

    return crud.swap_faq_order(db=db, faq1_id=faq1_id, faq2_id=faq2_id)


@settings.patch("/settings/faq/{faq_id}")
async def patch_faq(
        faq_id: UUID,
        updated_faq: schemas.UpdateFaq,
        db: Session = Depends(dep.get_db)
) -> schemas.Faq:
    if crud.get_faq(db=db, faq_id=faq_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Faq not found"})

    return crud.update_faq(db=db, faq_id=faq_id, updated_faq=updated_faq)


