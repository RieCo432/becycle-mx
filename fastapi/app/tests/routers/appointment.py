from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
import datetime

test_client = TestClient(app)


def test_request_appointment(clients, closed_days, client_auth_headers, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)

    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)
    for client, client_auth_header in zip(clients[:4], client_auth_headers[:4]):
        start_date_time = datetime.datetime.combine(future_date, datetime.time(17, 45))

        response = test_client.post("/appointments/request", json={
            "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "typeId": appointment_types[0].id,
            "notes": "test request",
        }, headers=client_auth_header)

        assert response.status_code == 200

        appointment = db.scalar(
            select(models.Appointment)
            .where(
                (models.Appointment.clientId == client.id)
                & (models.Appointment.startDateTime == start_date_time)
                & (models.Appointment.notes == "test request")
            )
        )

        assert response.json() == appointment

        future_date += relativedelta(days=1)
        while future_date.weekday() not in appointment_general_settings.openingDays or future_date in [cd.date for cd in closed_days]:
            future_date += relativedelta(days=1)


def test_request_appointment_too_many_pending(clients, client_auth_headers, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)

    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)

    start_date_time = datetime.datetime.combine(future_date, datetime.time(17, 45))

    response = test_client.post("/appointments/request", json={
        "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "typeId": appointment_types[0].id,
        "notes": "test request",
    }, headers=client_auth_headers[4])

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "You cannot have more than 2 pending appointment requests. Please wait for pending requests to get denied or accepted!"


def test_request_appointment_unavailable(clients, client_auth_headers, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)

    start_date_time = datetime.datetime.combine(future_date, datetime.time(16, 45))

    response = test_client.post("/appointments/request", json={
        "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "typeId": appointment_types[0].id,
        "notes": "test request",
    }, headers=client_auth_headers[0])

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Someone just requested this slot. Refreshing list... Please choose a new slot."


def test_create_appointment(clients, closed_days, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits, appointment_manager_user_auth_header):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)

    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)
    for client in clients[:4]:
        start_date_time = datetime.datetime.combine(future_date, datetime.time(17, 45))

        response = test_client.post("/appointments/new", json={
            "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "typeId": appointment_types[0].id,
            "notes": "test new appointment",
            "clientId": str(client.id)
        }, headers=appointment_manager_user_auth_header)

        assert response.status_code == 200

        appointment = db.scalar(
            select(models.Appointment)
            .where(
                (models.Appointment.clientId == client.id)
                & (models.Appointment.startDateTime == start_date_time)
                & (models.Appointment.notes == "test new appointment")
            )
        )

        assert response.json() == appointment

        future_date += relativedelta(days=1)
        while future_date.weekday() not in appointment_general_settings.openingDays or future_date in [cd.date for cd in closed_days]:
            future_date += relativedelta(days=1)


def test_create_appointment_too_many_pending(clients, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits, appointment_manager_user_auth_header):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)

    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)

    start_date_time = datetime.datetime.combine(future_date, datetime.time(17, 45))

    response = test_client.post("/appointments/new", json={
        "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "typeId": appointment_types[0].id,
        "notes": "test new appointment",
        "clientId": str(clients[4].id)
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "You cannot have more than 2 pending appointment requests. Please wait for pending requests to get denied or accepted!"


def test_create_appointment_unavailable(clients, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits, appointment_manager_user_auth_header):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while future_date.weekday() not in appointment_general_settings.openingDays:
        future_date += relativedelta(days=1)

    start_date_time = datetime.datetime.combine(future_date, datetime.time(16, 45))

    response = test_client.post("/appointments/new", json={
        "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "typeId": appointment_types[0].id,
        "notes": "test new appointment",
        "clientId": str(clients[0].id),
    }, headers=appointment_manager_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Someone just requested this slot. Refreshing list... Please choose a new slot."


def test_create_appointment_unavailable_ignore_limit(clients, closed_days, appointments, appointment_types, appointment_general_settings, appointment_concurrency_limits, appointment_manager_user_auth_header):
    future_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while future_date.weekday() not in appointment_general_settings.openingDays or future_date in [cd.date for cd in closed_days]:
        future_date += relativedelta(days=1)

    start_date_time = datetime.datetime.combine(future_date, datetime.time(16, 45))

    response = test_client.post("/appointments/new", json={
        "startDateTime": start_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "typeId": appointment_types[0].id,
        "notes": "test new appointment",
        "clientId": str(clients[0].id),
    }, params={"ignore_limits": True}, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200

    appointment = db.scalar(
        select(models.Appointment)
        .where(
            (models.Appointment.clientId == clients[0].id)
            & (models.Appointment.startDateTime == start_date_time)
            & (models.Appointment.notes == "test new appointment")
        )
    )

    assert response.json() == appointment


def test_confirm_appointment(appointments, appointment_manager_user_auth_header):
    for appointment in appointments:
        response = test_client.patch("/appointments/{appointmentId}/confirm".format(appointmentId=appointment.id), headers=appointment_manager_user_auth_header)

        if appointment.startDateTime > datetime.datetime.utcnow():
            assert response.status_code == 200
            db.refresh(appointment)
            assert response.json() == appointment
            assert appointment.confirmed
        else:
            was_appointment_confirmed_already = appointment.confirmed
            assert response.status_code == 400
            assert response.json().get("detail").get("description") == "This appointment does not exist or is in the past."
            db.refresh(appointment)
            assert appointment.confirmed == was_appointment_confirmed_already


def test_cancel_appointment(appointments, appointment_manager_user_auth_header):
    for appointment in appointments:
        response = test_client.patch("/appointments/{appointmentId}/cancel".format(appointmentId=appointment.id), headers=appointment_manager_user_auth_header)

        if appointment.startDateTime > datetime.datetime.utcnow():
            assert response.status_code == 200
            assert response.json() != appointment
            db.refresh(appointment)
            assert response.json() == appointment
        else:
            was_appointment_cancelled_already = appointment.cancelled
            assert response.status_code == 400
            assert response.json().get("detail").get("description") == "This appointment does not exist or is in the past."
            db.refresh(appointment)
            assert appointment.cancelled == was_appointment_cancelled_already


def test_get_available_appointments_lending(appointments, closed_days, appointment_general_settings, appointment_concurrency_limits, appointment_types):
    days = []
    next_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while next_date <= datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.maxBookAhead):
        if next_date.weekday() in appointment_general_settings.openingDays and next_date not in [cd.date for cd in closed_days]:
            days.append(next_date.strftime("%Y-%m-%d"))
        next_date += relativedelta(days=1)

    expected_availability = {
        days[0]: [
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True}
        ],
        days[1]: [
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True}
        ],
        **{d: [
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
        ] for d in days[2:]},
    }

    response = test_client.get("/appointments/available", params={"appointment_type_id": appointment_types[0].id})

    assert response.status_code == 200
    assert response.json() == expected_availability


def test_get_available_appointments_repair(appointments, closed_days, appointment_general_settings, appointment_concurrency_limits, appointment_types):
    days = []
    next_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while next_date <= datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.maxBookAhead):
        if next_date.weekday() in appointment_general_settings.openingDays and next_date not in [cd.date for cd in closed_days]:
            days.append(next_date.strftime("%Y-%m-%d"))
        next_date += relativedelta(days=1)

    expected_availability = {
        days[0]: [
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
        ],
        days[1]: [
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
        ],
        **{d: [
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
        ] for d in days[2:]},
    }

    response = test_client.get("/appointments/available", params={"appointment_type_id": appointment_types[1].id})

    assert response.status_code == 200
    assert response.json() == expected_availability


def test_get_available_appointments_lending_ignore_limits(appointments, closed_days, appointment_general_settings, appointment_concurrency_limits, appointment_types, appointment_manager_user_auth_header):
    days = []
    next_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while next_date <= datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.maxBookAhead):
        if next_date.weekday() in appointment_general_settings.openingDays and next_date not in [cd.date for cd in closed_days]:
            days.append(next_date.strftime("%Y-%m-%d"))
        next_date += relativedelta(days=1)

    expected_availability = {
        days[0]: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ],
        days[1]: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ],
        **{d: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ] for d in days[2:]}
    }

    response = test_client.get("/appointments/available", params={"ignore_limits": True, "appointment_type_id": appointment_types[0].id}, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_availability


def test_get_available_appointments_repair_ignore_limits(appointments, closed_days, appointment_general_settings, appointment_concurrency_limits, appointment_types, appointment_manager_user_auth_header):
    days = []
    next_date = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while next_date <= datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.maxBookAhead):
        if next_date.weekday() in appointment_general_settings.openingDays and next_date not in [cd.date for cd in closed_days]:
            days.append(next_date.strftime("%Y-%m-%d"))
        next_date += relativedelta(days=1)

    expected_availability = {
        days[0]: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ],
        days[1]: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ],
        **{d: [
            {"time": datetime.time(16, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(16, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(16, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(17, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 0).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 15).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 30).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(18, 45).strftime("%H:%M:%S"), "available": True},
            {"time": datetime.time(19, 0).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 15).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 30).strftime("%H:%M:%S"), "available": False},
            {"time": datetime.time(19, 45).strftime("%H:%M:%S"), "available": False}
        ] for d in days[2:]},
    }

    response = test_client.get("/appointments/available", params={"ignore_limits": True, "appointment_type_id": appointment_types[1].id}, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_availability


def test_get_appointment_types_include_inactive(appointment_types):
    response = test_client.get("/appointments/types", params={"inactive": True})

    assert response.status_code == 200
    assert response.json() == appointment_types


def test_get_appointment_types(appointment_types):
    response = test_client.get("/appointments/types")

    assert response.status_code == 200
    assert response.json() == [at for at in appointment_types if at.active]


def test_create_appointment_type(appointment_types, appointment_manager_user_auth_header):
    new_type = {
        "id": "test",
        "active": True,
        "title": "New Appointment Type",
        "description": "New Appointment Type Description",
        "duration": 45,
    }

    response = test_client.post("/appointments/types", json=new_type, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    assert response.json() == new_type

    assert db.scalar(
        select(models.AppointmentType)
        .where(models.AppointmentType.id == "test")
    ) == response.json()


def test_create_appointment_type_already_exists(appointment_types, appointment_manager_user_auth_header):
    new_type = {
        "id": "mrep",
        "active": True,
        "title": "New Appointment Type",
        "description": "New Appointment Type Description",
        "duration": 45,
    }

    response = test_client.post("/appointments/types", json=new_type, headers=appointment_manager_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This appointment type ID already exists!"


def test_get_appointment_type(appointment_types):
    for appointment_type in appointment_types:
        response = test_client.get("/appointments/types/{typeId}".format(typeId=appointment_type.id))

        assert response.status_code == 200
        assert response.json() == appointment_type


def test_update_appointment_type(appointment_types, appointment_manager_user_auth_header):
    new_info = {
        "active": False,
        "description": "This is a new description",
        "duration": 90,
        "title": "New Title"
    }

    response = test_client.patch("/appointments/types/{typeId}".format(typeId=appointment_types[0].id), json=new_info, headers=appointment_manager_user_auth_header)

    assert response.status_code == 200
    assert response.json() == {"id": appointment_types[0].id, **new_info}
    assert response.json() != appointment_types[0]
    db.refresh(appointment_types[0])
    assert response.json() == appointment_types[0]


def test_get_appointments_next_7_days(appointments, closed_days, normal_user_auth_header):
    appointments_in_period = [a for a in appointments if datetime.datetime.utcnow() <= a.startDateTime and a.endDateTime <= datetime.datetime.utcnow() + relativedelta(weeks=1) and not a.cancelled]
    closed_days_in_period = [cd for cd in closed_days if datetime.datetime.utcnow().date() <= cd.date <= (datetime.datetime.utcnow() + relativedelta(weeks=1)).date()]

    response = test_client.get("/appointments/calendar", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    closed_days_in_response = [datetime.datetime.strptime(event.get("startDateTime"), "%Y-%m-%dT%H:%M:%S").date() for event in response_json if event.get("typeId") == "closedDay"]

    assert len(response_json) == len(appointments_in_period) + len(closed_days_in_period)

    assert all([a in response_json for a in appointments_in_period])
    assert all([cd_r in [cd.date for cd in closed_days_in_period] for cd_r in closed_days_in_response])


def test_get_appointments_between_7_and_14_days_from_now(appointments, closed_days, normal_user_auth_header):
    appointments_in_period = [a for a in appointments if datetime.datetime.utcnow() + relativedelta(weeks=1) <= a.startDateTime <= datetime.datetime.utcnow() + relativedelta(weeks=2) and not a.cancelled]
    closed_days_in_period = [cd for cd in closed_days if (datetime.datetime.utcnow() + relativedelta(weeks=1)).date() <= cd.date <= (datetime.datetime.utcnow() + relativedelta(weeks=2)).date()]

    response = test_client.get("/appointments/calendar", params={
        "start_datetime": (datetime.datetime.utcnow() + relativedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%S"),
        "end_datetime": (datetime.datetime.utcnow() + relativedelta(weeks=2)).strftime("%Y-%m-%dT%H:%M:%S")
    }, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    closed_days_in_response = [datetime.datetime.strptime(event.get("startDateTime"), "%Y-%m-%dT%H:%M:%S").date() for event in response_json if event.get("typeId") == "closedDay"]

    assert len(response_json) == len(appointments_in_period) + len(closed_days_in_period)

    assert all([a in response_json for a in appointments_in_period])
    assert all([cd_r in [cd.date for cd in closed_days_in_period] for cd_r in closed_days_in_response])
