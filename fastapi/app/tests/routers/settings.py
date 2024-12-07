from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
import datetime

test_client = TestClient(app)


def test_get_appointment_general_settings(appointment_general_settings, normal_user_auth_header):
    response = test_client.get("/settings/appointments/general", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("openingDays") == appointment_general_settings.openingDays
    assert response_json.get("minBookAhead") == appointment_general_settings.minBookAhead
    assert response_json.get("maxBookAhead") == appointment_general_settings.maxBookAhead
    assert response_json.get("slotDuration") == appointment_general_settings.slotDuration


def test_update_appointment_general_settings(appointment_general_settings, appointment_manager_user_auth_header):
    response = test_client.patch("/settings/appointments/general", json={
        "openingDays": [1, 3],
        "minBookAhead": 10,
        "maxBookAhead": 80,
        "slotDuration": 30,
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("openingDays") == [1, 3]
    assert response_json.get("minBookAhead") == 10
    assert response_json.get("maxBookAhead") == 80
    assert response_json.get("slotDuration") == 30


def test_get_appointment_concurrency_limits(appointment_concurrency_limits, normal_user_auth_header):
    response = test_client.get("/settings/appointments/concurrency", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len(appointment_concurrency_limits)
    assert all([acl in appointment_concurrency_limits for acl in response_json])


def test_create_appointment_concurrency_limit_already_set(appointment_concurrency_limits, appointment_manager_user_auth_header):
    new_limit = {
        "afterTime": datetime.time(hour=17, minute=30).strftime("%H:%M:%S"),
        "maxConcurrent": 2
    }

    response = test_client.post("/settings/appointments/concurrency", json=new_limit, headers=appointment_manager_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "There already is a concurrency limit for this time!"


def test_create_appointment_concurrency_limit(appointment_concurrency_limits, appointment_manager_user_auth_header):
    new_limit = {
        "afterTime": datetime.time(hour=18, minute=0).strftime("%H:%M:%S"),
        "maxConcurrent": 2
    }

    response = test_client.post("/settings/appointments/concurrency", json=new_limit, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    new_limit_db = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=18, minute=0))
    )

    assert response.json() == new_limit_db


def test_delete_appointment_concurrency_limit_not_exist(appointment_concurrency_limits, appointment_manager_user_auth_header):
    response = test_client.delete("/settings/appointments/concurrency/18:00", headers=appointment_manager_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "This appointment concurrency does not exist!"


def test_delete_appointment_concurrency_limit(appointment_concurrency_limits,
                                                        appointment_manager_user_auth_header):
    response = test_client.delete("/settings/appointments/concurrency/17:30",
                                  headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    assert db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=17, minute=30))
    ) is None


def test_update_appointment_concurrency_limit_change_limit(appointment_concurrency_limits, appointment_manager_user_auth_header):
    response = test_client.patch("/settings/appointments/concurrency/17:30", json={
        "maxConcurrent": 6
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    db.refresh(appointment_concurrency_limits[2])
    assert response.json() == appointment_concurrency_limits[2]
    assert appointment_concurrency_limits[2].maxConcurrent == 6


def test_update_appointment_concurrency_limit_change_aftertime(appointment_concurrency_limits, appointment_manager_user_auth_header):
    old_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit.maxConcurrent)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=17, minute=30))
    )

    response = test_client.patch("/settings/appointments/concurrency/17:30", json={
        "afterTime": "18:00"
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    assert db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=17, minute=30))
    ) is None

    new_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=18, minute=0))
    )

    assert new_limit == response.json()
    assert new_limit.maxConcurrent == old_limit


def test_update_appointment_concurrency_limit_change_aftertime_and_limit(appointment_concurrency_limits, appointment_manager_user_auth_header):
    old_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit.maxConcurrent)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=17, minute=30))
    )

    response = test_client.patch("/settings/appointments/concurrency/17:30", json={
        "afterTime": "18:00",
        "maxConcurrent": 6
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    assert db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=17, minute=30))
    ) is None

    new_limit = db.scalar(
        select(models.AppointmentConcurrencyLimit)
        .where(models.AppointmentConcurrencyLimit.afterTime == datetime.time(hour=18, minute=0))
    )

    assert new_limit == response.json()
    assert new_limit.maxConcurrent != old_limit


def test_update_appointment_concurrency_limit_not_exist(appointment_concurrency_limits, appointment_manager_user_auth_header):
    response = test_client.patch("/settings/appointments/concurrency/17:15", json={
        "maxConcurrent": 6
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "There is no limit for this time!"


def test_update_appointment_concurrency_limit_change_aftertime_to_already_existing(appointment_concurrency_limits, appointment_manager_user_auth_header):
    response = test_client.patch("/settings/appointments/concurrency/17:30", json={
        "afterTime": "16:15"
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Is there already a limit for this time?"


def test_get_closed_days(closed_days, normal_user_auth_header):
    response = test_client.get("/settings/closed-days", headers=normal_user_auth_header)

    assert response.status_code == 200
    assert len(response.json()) == len(closed_days)
    assert all([cd in closed_days for cd in response.json()])


def test_create_closed_day(closed_days, appointment_general_settings, appointment_manager_user_auth_header):
    future_date = datetime.datetime.utcnow().date() + relativedelta(months=2)
    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)

    response = test_client.post("/settings/closed-day", json={
        "date": future_date.strftime("%Y-%m-%d"),
        "note": "Test add closed day"
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    new_cd = db.scalar(
        select(models.ClosedDay)
        .where(
            (models.ClosedDay.date == future_date)
            & (models.ClosedDay.note == "Test add closed day")
        )
    )

    assert response.json() == new_cd


def test_create_closed_day_already_closed(closed_days, appointment_general_settings, appointment_manager_user_auth_header):
    response = test_client.post("/settings/closed-day", json={
        "date": closed_days[0].date.strftime("%Y-%m-%d"),
        "note": "Test add closed day"
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This day is already closed."


def test_delete_closed_day(closed_days, appointment_manager_user_auth_header):
    response = test_client.delete("/settings/closed-day/{date}".format(date=closed_days[0].date.strftime("%Y-%m-%d")), headers=appointment_manager_user_auth_header)
    assert response.status_code == 200

    assert db.scalar(
        select(models.ClosedDay)
        .where(models.ClosedDay.date == closed_days[0].date)
    ) is None


def test_delete_closed_day_not_exist(closed_days, appointment_manager_user_auth_header):
    response = test_client.delete("/settings/closed-day/{date}".format(date="2022-06-13"), headers=appointment_manager_user_auth_header)
    assert response.status_code == 400

    assert response.json().get("detail").get("description") == "This date is not registered as a closed day."


def test_update_address(address, admin_user_auth_header):
    response = test_client.put("/settings/address", json={
        "number": "69",
        "street": "Sixty-Nine Street",
        "postcode": "NC12 3CD",
        "city": "Newcastle"
    }, headers=admin_user_auth_header)

    assert response.status_code == 200
    db.refresh(address)
    assert response.json() == address
    assert address.number == "69"
    assert address.street == "Sixty-Nine Street"
    assert address.postcode == "NC12 3CD"
    assert address.city == "Newcastle"


def test_add_contract_type(contract_types, admin_user_auth_header):
    response = test_client.post("/settings/contract-types", json={
        "id": "new-contract-type"
    }, headers=admin_user_auth_header)

    assert response.status_code == 200
    new_type_db = db.scalar(
        select(models.ContractType)
        .where(models.ContractType.id == "new-contract-type")
    )
    assert new_type_db.id == response.json().get("id")


def test_add_contract_type_already_exists(contract_types, admin_user_auth_header):
    response = test_client.post("/settings/contract-types", json={
        "id": "refugee"
    }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This contract type already exists!"


def test_delete_contract_type(contract_types, admin_user_auth_header):
    response = test_client.delete("/settings/contract-types/{contractTypeId}".format(contractTypeId=contract_types[0].id), headers=admin_user_auth_header)

    assert response.status_code == 200
    assert response.json().get("id") == contract_types[0].id
    assert db.scalar(
        select(models.ContractType)
        .where(models.ContractType.id == contract_types[0].id)
    ) is None


def test_add_expense_type(expense_types, admin_user_auth_header):
    response = test_client.post("/settings/expense-types", json={
        "id": "newtype",
        "description": "New Expense Type"
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    new_expense_type_db = db.scalar(
        select(models.ExpenseType)
        .where(models.ExpenseType.id == "newtype")
    )

    assert response.json().get("id") == new_expense_type_db.id
    assert response.json().get("description") == new_expense_type_db.description


def test_add_expense_type_already_exists(expense_types, admin_user_auth_header):
    response = test_client.post("/settings/expense-types", json={
        "id": expense_types[0].id,
        "description": "New Expense Type"
    }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This expense type already exists!"


def test_delete_expense_type(expense_types, admin_user_auth_header):
    response = test_client.delete("/settings/expense-types/{expenseTypeId}".format(expenseTypeId=expense_types[0].id), headers=admin_user_auth_header)

    assert response.status_code == 200
    assert response.json().get("id") == expense_types[0].id
    assert response.json().get("description") == expense_types[0].description
    assert db.scalar(
        select(models.ExpenseType)
        .where(models.ExpenseType.id == expense_types[0].id)
    ) is None


def test_update_expense_type(expense_types, admin_user_auth_header):
    response = test_client.patch("/settings/expense-types/{expenseTypeId}".format(expenseTypeId=expense_types[0].id), json={
        "description": "New description"
    }, headers=admin_user_auth_header)

    assert response.status_code == 200
    db.refresh(expense_types[0])
    assert response.json().get("id") == expense_types[0].id
    assert response.json().get("description") == expense_types[0].description
    assert expense_types[0].description == "New description"
