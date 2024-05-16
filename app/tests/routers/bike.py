from fastapi.testclient import TestClient
from app.tests.pytestFixtures import *
from app.main import app
from sqlalchemy import select

client = TestClient(app)

clear_database()


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
