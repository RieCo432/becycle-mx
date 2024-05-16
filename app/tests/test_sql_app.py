import datetime

from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient
from .pytestFixtures import *
from app.main import app
from fastapi import Depends
import app.dependencies as dep
import asyncio
from sqlalchemy import select

client = TestClient(app)

clear_database()


'''
Test Public Router
'''


def test_get_opening_times(appointment_concurrency_limits, appointment_general_settings):
    response = client.get("/public/opening-times")
    assert response.status_code == 200
    assert response.json() == [
        {"day": "Monday", "open": "16:15", "close": "19:45"},
        {"day": "Wednesday", "open": "16:15", "close": "19:45"}
    ]


def test_get_opening_days(appointment_general_settings):
    response = client.get("/public/opening-days")
    assert response.status_code == 200
    assert response.json() == [0, 2]


def test_get_opening_hours(appointment_concurrency_limits):
    response = client.get("/public/opening-hours")
    assert response.status_code == 200
    assert response.json() == {"open_time": "16:15:00", "close_time": "19:45:00"}


def test_get_slot_duration(appointment_general_settings):
    response = client.get("/public/slot-duration")
    assert response.status_code == 200
    assert response.json() == 15


def test_get_next_closed_day(closed_days):
    response = client.get("/public/next-closed-day")

    next_closed_date = str(datetime.datetime.utcnow().date() + relativedelta(days=7))

    assert response.status_code == 200
    assert response.json() == {"date": next_closed_date, "note": "Workshop Day"}


def test_get_address(address):
    response = client.get("/public/address")
    assert response.status_code == 200
    assert response.json() == {"number": "21-23", "street": "High Street", "postcode": "AB24 3EE", "city": "Aberdeen"}


def test_get_user_presentation_cards(user_presentation_cards):
    response = client.get("/public/users/presentation-cards")
    assert response.status_code == 200
    assert all(
        [
            response_card == {
                "bio": user_presentation_card.bio,
                "id": str(user_presentation_card.id),
                "name": user_presentation_card.name,
                "photoContentType": user_presentation_card.photoContentType
            } for response_card, user_presentation_card in zip(
                response.json(),
                [user_presentation_card for user_presentation_card in user_presentation_cards if
                    not user_presentation_card.user.softDeleted]
            )
        ])

# def get_user_presentation_card_photo():


'''
Test User Router
'''


@pytest.mark.asyncio
async def test_get_user_token_correct_password(users):
    for user in users:
        response = client.post("/users/token", data={
            "username": user.username,
            "password": f"{user.username}1234"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        if not user.softDeleted:
            assert response.status_code == 200
            response_json = response.json()

            user_authenticated = await dep.get_current_user(token=response_json.get("access_token"), db=db)

            assert user_authenticated.id == user.id
        else:
            assert response.status_code == 400
            assert response.json().get("detail").get("description") == "User has been soft-deleted"


def test_get_user_token_incorrect_password(users):
    for user in users:
        response = client.post("/users/token", data={
            "username": user.username,
            "password": "wrong_password"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        assert response.status_code == 400
        assert response.json().get("detail").get("description") == "Incorrect username or password"


def test_get_user_token_invalid_password_default(users):
    for user in users:
        response = client.post("/users/token", data={
            "username": user.username,
            "password": "password"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        assert response.status_code == 400
        assert response.json().get("detail").get("description") == "Cannot login with default password. Please contact an admin to set a password!"


'''
Test Bike Router
'''


def test_find_bike(bikes, normal_user_auth_header):
    for bike in bikes:
        response = client.get("/bike/find", params={
            "make": bike.make,
            "model": bike.model,
            "colour": bike.colour,
            "decals": bike.decals,
            "serial_number": bike.serialNumber
        }, headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == bike


def test_find_bikes(bikes, normal_user_auth_header):
    response = client.get("/bikes/find", params={
        "make": "apol",
        "serial_number": "abcd1"
    }, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert all([response_bike in bikes[:2] for response_bike in response_json])


def test_get_bikes(bikes, normal_user_auth_header):
    response = client.get("/bikes", headers=normal_user_auth_header)

    assert response.status_code == 200
    assert len(response.json()) == len(bikes)
    assert all([response_bike in bikes for response_bike in response.json()])


def test_get_bike(bikes):
    for bike in bikes:
        response = client.get("/bikes/{bikeId}".format(bikeId=bike.id))
        assert response.status_code == 200
        json_response = response.json()
        assert json_response == bike


def test_patch_bike(bikes, normal_user_auth_header):
    response = client.patch("/bikes/{bikeId}".format(bikeId=bikes[0].id), json={
            "make": "NewMake",
            "model": "NewModel",
            "colour": "NewColour",
            "decals": "NewDecals",
            "serialNumber": "NewSerialNumber"
        }, headers=normal_user_auth_header)

    assert response.status_code == 200
    db.refresh(bikes[0])
    assert response.json() == bikes[0]


def test_get_bike_contracts(bikes, contracts, normal_user_auth_header):
    for bike in bikes:
        response = client.get("/bikes/{bikeId}/contracts".format(bikeId=bike.id), headers=normal_user_auth_header)

        assert response.status_code == 200

        assert len(response.json()) == len(bike.contracts)
        assert all([response_contract in bike.contracts for response_contract in response.json()])


def test_post_bike(bikes, normal_user_auth_header):
    new_bike = {
        "make": "NewBikeMake",
        "model": "NewBikeModel",
        "colour": "NewBikeColour",
        "decals": "NewBikeDecals",
        "serialNumber": "NewBikeSerialNumber"
    }
    bike_in_db = db.scalar(
        select(models.Bike)
        .where(models.Bike.make == new_bike["make"].lower())
    )

    assert bike_in_db is None

    response = client.post("/bike", json=new_bike, headers=normal_user_auth_header)

    response_json = response.json()
    assert response.status_code == 200
    assert all([
        response_json[k] == new_bike[k].lower() for k in new_bike.keys()
    ])

    bike_in_db = db.scalar(
        select(models.Bike)
        .where(models.Bike.make == new_bike["make"].lower())
    )

    assert response_json == bike_in_db
