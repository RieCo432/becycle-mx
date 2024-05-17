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


def test_get_make_suggestions(bikes, normal_user_auth_header):
    queries = ["r", "ral", "rev", "e", "eleph", "a", "apo", "avi", "ol"]
    all_expected_suggestions = [set([bike.make for bike in bikes if query.lower() in bike.make]) for query in queries]

    for query, expected_suggestions in zip(queries, all_expected_suggestions):
        response = client.get("/bikes/suggest/makes", params={"make": query}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(expected_suggestions)
        assert all([suggestion in expected_suggestions for suggestion in response_json])


def test_get_model_suggestions(bikes, normal_user_auth_header):
    queries = ["s", "ski","spo", "e", "exc", "eni", "a", "ame", "af", "c", "chl", "cui", "h", "hea"]
    all_expected_suggestions = [set([bike.model for bike in bikes if query.lower() in bike.model]) for query in queries]

    for query, expected_suggestions in zip(queries, all_expected_suggestions):
        response = client.get("/bikes/suggest/models", params={"model": query}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(expected_suggestions)
        assert all([suggestion in expected_suggestions for suggestion in response_json])


def test_get_serial_number_suggestions(bikes, normal_user_auth_header):
    queries = ["a", "e", "i", "m", "q", "u", "ab", "ef", "ij", "mn", "qr", "uv", "abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx", "1", "5", "9", "3", "7", "23", "45", "56", "89"]
    all_expected_suggestions = [set([bike.serialNumber for bike in bikes if query.lower() in bike.serialNumber]) for query in queries]

    for query, expected_suggestions in zip(queries, all_expected_suggestions):
        response = client.get("/bikes/suggest/serial-numbers", params={"serial_number": query}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(expected_suggestions)
        assert all([suggestion in expected_suggestions for suggestion in response_json])


def test_get_colour_suggestions(bikes, normal_user_auth_header):
    queries = ["b", "p", "br", "bl", "blu", "bla", "pi", "pur"]
    all_expected_suggestions = [set([bike.colour for bike in bikes if query.lower() in bike.colour]) for query in queries]

    for query, expected_suggestions in zip(queries, all_expected_suggestions):
        response = client.get("/bikes/suggest/colours", params={"colour": query}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(expected_suggestions)
        assert all([suggestion in expected_suggestions for suggestion in response_json])


def test_get_bike_conditions(normal_user_auth_header):
    expected_conditions = ["poor", "fair", "good", "excellent"]
    response = client.get("/bike/conditions", headers=normal_user_auth_header)

    assert response.status_code == 200
    assert all([ec in response.json() for ec in expected_conditions])
