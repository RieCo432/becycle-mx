from random import random

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
from datetime import datetime

CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES = int(os.environ['CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES'])

test_client = TestClient(app)


def test_get_clients_single_result_first_name(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "alice"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[0]]


def test_get_clients_single_result_last_name(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"last_name": "frank"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[1]]


def test_get_clients_multiple_results_last_name(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"last_name": "smith"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len(clients[3:])
    assert all([response_client in clients[3:] for response_client in response_json])


def test_get_clients_single_result_email_address(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"email_address": "charlie.maurice@example.com"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[2]]


def test_get_clients_single_result_full_name(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "alice", "last_name": "humphrey"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[0]]


def test_get_clients_single_result_first_name_email(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "bob", "email_address": "bob.frank@example.com"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[1]]


def test_get_clients_single_result_last_name_email(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"last_name": "maurice", "email_address": "charlie.maurice@example.com"}, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[2]]


def test_get_clients_multiple_result_full_name_email(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "debby", "last_name": "smith", "email_address": "debby.smith@example.com"},
                               headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == clients[3:]


def test_get_clients_single_result_full_name_email(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "alice", "last_name": "humphrey", "email_address": "alice.humphrey@example.com"},
                               headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json() == [clients[0]]


def test_get_clients_no_result_full_name_email(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "not", "last_name": "existing", "email_address": "not.existing@example.com"},
                               headers=normal_user_auth_header)
    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "No clients"


def test_get_clients_no_result_first_name(clients: list[models.Client], normal_user_auth_header):
    response = test_client.get("/clients", params={"first_name": "notexisting"},
                               headers=normal_user_auth_header)
    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "No clients"


def test_get_client_id_by_email(clients: list[models.Client], normal_user_auth_header):
    for client in clients:
        response = test_client.get("/client/id-by-email", params={"email_address": client.emailAddress}, headers=normal_user_auth_header)
        assert response.status_code == 200
        assert response.json().get("id") == str(client.id)


def test_get_client_email_address_suggestions(clients: list[models.Client], normal_user_auth_header):
    queries = ["a", "b", "c", "d", "al", "bo", "cha", "de", "ali", "ale", "who", "when"]
    for query in queries:
        expected_suggestions = [client.emailAddress for client in clients if client.emailAddress.startswith(query)]
        response = test_client.get("/clients/email-address-suggestions", params={"email_address": query}, headers=normal_user_auth_header)
        assert response.status_code == 200
        assert set(response.json()) == set(expected_suggestions)


def test_post_client(clients, normal_user_auth_header):
    assert db.scalar(
        select(models.Client)
        .where(models.Client.firstName == "new")
    ) is None

    new_client_json = {
        "firstName": "New",
        "lastName": "Client",
        "emailAddress": "New.Client@example.com"
    }

    response = test_client.post("/client", json=new_client_json, headers=normal_user_auth_header)
    assert response.status_code == 200
    assert response.json().get("firstName") == new_client_json["firstName"].lower()
    assert response.json().get("lastName") == new_client_json["lastName"].lower()
    assert response.json().get("emailAddress") == new_client_json["emailAddress"].lower()

    new_client = db.scalar(
        select(models.Client)
        .where(models.Client.firstName == "new")
    )

    assert response.json() == new_client


def test_create_client_temp_new(clients_temp):
    new_client_temp = {"firstName": "John", "lastName": "Doe", "emailAddress": "john.doe@example.com"}
    response = test_client.post("/client/temp", json=new_client_temp)
    assert response.status_code == 200
    assert response.json().get("firstName") == new_client_temp["firstName"].lower()
    assert response.json().get("lastName") == new_client_temp["lastName"].lower()
    assert response.json().get("emailAddress") == new_client_temp["emailAddress"].lower()
    assert datetime.strptime(response.json().get("expirationDateTime"), "%Y-%m-%dT%H:%M:%S.%f") <= datetime.utcnow() + relativedelta(minutes=CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES)


def test_create_client_temp_overwrite(clients_temp):
    client_temp = {"firstName": clients_temp[0].firstName, "lastName": clients_temp[0].lastName, "emailAddress": clients_temp[0].emailAddress}
    response = test_client.post("/client/temp", json=client_temp)
    assert response.status_code == 200

    assert response.json().get("id") != str(clients_temp[0].id)
    assert response.json().get("firstName") == client_temp["firstName"]
    assert response.json().get("lastName") == client_temp["lastName"]
    assert response.json().get("emailAddress") == client_temp["emailAddress"]
    assert datetime.strptime(response.json().get("expirationDateTime"), "%Y-%m-%dT%H:%M:%S.%f") <= datetime.utcnow() + relativedelta(minutes=CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES)

    assert db.scalar(
        select(models.ClientTemp)
        .where(models.ClientTemp.id == clients_temp[0].id)
    ) is None


def test_verify_client_temp_invalid_verification_code(clients_temp):
    random_code = "{:06d}".format(int(random() * 1000000))
    while random_code == clients_temp[0].verificationCode:
        random_code = "{:06d}".format(int(random() * 1000000))

    response = test_client.post("/client/temp/verify", data={"client_temp_id": clients_temp[0].id, "verification_code": random_code},
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This code is invalid."


def test_verify_client_temp_expired_verification_code(clients_temp):
    response = test_client.post("/client/temp/verify",
                                data={"client_temp_id": clients_temp[1].id, "verification_code": clients_temp[1].verificationCode},
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This action has expired."


def test_verify_client_temp(clients_temp):
    response = test_client.post("/client/temp/verify",
                                data={"client_temp_id": clients_temp[0].id,
                                      "verification_code": clients_temp[0].verificationCode},
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200

    response_me = test_client.get("/clients/me", headers={"Authorization": "Bearer " + response.json().get("access_token")})
    assert response_me.status_code == 200
    assert response_me.json().get("firstName") == clients_temp[0].firstName
    assert response_me.json().get("lastName") == clients_temp[0].lastName
    assert response_me.json().get("emailAddress") == clients_temp[0].emailAddress

    assert db.scalar(
        select(models.ClientTemp)
        .where(models.ClientTemp.id == clients_temp[0].id)
    ) is None
