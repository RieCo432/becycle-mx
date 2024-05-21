from random import random

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
from datetime import datetime
import re

CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES = int(os.environ["CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES"])
CLIENT_LOGIN_CODE_EXPIRE_MINUTES = int(os.environ["CLIENT_LOGIN_CODE_EXPIRE_MINUTES"])

test_client = TestClient(app)


def get_6_random_digits():
    return "{:06d}".format(int(random() * 1000000))


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

    client_temp = db.scalar(
        select(models.ClientTemp)
        .where(models.ClientTemp.id == response.json().get("id"))
    )

    assert re.fullmatch(r"[0-9]{6}", client_temp.verificationCode)


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

    client_temp = db.scalar(
        select(models.ClientTemp)
        .where(models.ClientTemp.id == response.json().get("id"))
    )

    assert re.fullmatch(r"[0-9]{6}", client_temp.verificationCode)


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


def test_get_client_login_code_not_exist(clients):
    response = test_client.get("/client/login-code", params={"email_address": "doesnot.exist@example.com"})

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "There is no client associated with this email address."


def test_get_client_login_code(clients, client_logins):
    for client in clients:
        response = test_client.get("/client/login-code", params={"email_address": client.emailAddress})

        assert response.status_code == 200
        assert response.json().get("id") == str(client.id)

        client_login = db.scalar(
            select(models.ClientLogin)
            .where(models.ClientLogin.clientId == client.id)
        )

        assert re.fullmatch(r"[0-9]{6}", client_login.code)
        assert client_login.expirationDateTime <= datetime.utcnow() + relativedelta(minutes=CLIENT_LOGIN_CODE_EXPIRE_MINUTES)


def test_get_token_no_login_requested(clients, client_logins):
    for client in [client for client in clients if client.id not in [client_login.clientId for client_login in client_logins]]:
        response = test_client.post("/clients/token", data={"username": str(client.id), "password": get_6_random_digits()})

        assert response.status_code == 404
        assert response.json().get("detail").get("description") == "This ID does not correspond to any client, or this client has not requested a login!"


def test_get_token_invalid_code(clients, client_logins):
    for client_login in client_logins:
        invalid_code = get_6_random_digits()
        while invalid_code == client_login.code:
            invalid_code = get_6_random_digits()
        response = test_client.post("/clients/token", data={"username": str(client_login.clientId), "password": invalid_code})

        assert response.status_code == 400
        assert response.json().get("detail").get("description") == "This code is not valid."


def test_get_token_expired_code(clients, client_logins_expired):
    for client_login_expired in client_logins_expired:
        response = test_client.post("/clients/token", data={"username": str(client_login_expired.clientId), "password": client_login_expired.code})

        assert response.status_code == 400
        assert response.json().get("detail").get("description") == "This code has expired."


def test_get_token(clients, client_logins):
    for client_login in client_logins:
        response = test_client.post("/clients/token", data={"username": str(client_login.clientId), "password": client_login.code})

        assert response.status_code == 200
        assert response.json().get("token_type") == "bearer"
        assert response.json().get("access_token", None) is not None


def test_find_client(clients, normal_user_auth_header):
    queries = [
        {"first_name": "ali", "last_name": "humph", "email_address": "alice.hump"},
        {"first_name": "bo", "last_name": "fran", "email_address": "bob.frank@"},
        {"first_name": "charli", "last_name": "mauri", "email_address": "charlie.mau"},
        {"first_name": "deb", "last_name": "smit", "email_address": "debby.sm"},
        {"first_name": "ale", "last_name": "smi", "email_address": "alex.smith@"},
        {"first_name": "al"},
        {"email_address": "al"},
        {"first_name": "al", "last_name": "sm"},
        {"last_name": "smith"},
        {"last_name": "frank"},
        {"first_name": "who"},
        {"last_name": "this"},
        {"email_address": "who.this@ex"}
    ]

    expected_suggestions_s = [
        [clients[0]],
        [clients[1]],
        [clients[2]],
        [clients[3], clients[4]],
        [clients[3], clients[4]],
        [clients[0], clients[4]],
        [clients[0], clients[4]],
        [clients[0], clients[3], clients[4]],
        [clients[3], clients[4]],
        [clients[1]],
        [],
        [],
        []
    ]

    for query, expected_suggestions in zip(queries, expected_suggestions_s):
        response = test_client.get("/clients/find", params=query, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(expected_suggestions)
        assert all([response_client in expected_suggestions for response_client in response_json])


def test_get_client_me(clients, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        response = test_client.get("/clients/me", headers=client_auth_header)

        assert response.status_code == 200
        assert response.json() == client


def test_update_client_me(clients, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        response = test_client.patch("/clients/me", json={"firstName": "New", "lastName": "Name"}, headers=client_auth_header)

        assert response.status_code == 200
        assert response.json() != client
        assert response.json().get("firstName") == "new"
        assert response.json().get("lastName") == "name"

        db.refresh(client)

        assert response.json() == client


def test_get_my_contracts_all(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id]
        response = test_client.get("/clients/me/contracts", headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_open(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and c.endDate >= datetime.utcnow().date() and c.returnedDate is None]
        response = test_client.get("/clients/me/contracts", params={"closed": False, "expired": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_expired(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and c.endDate < datetime.utcnow().date() and c.returnedDate is None]
        response = test_client.get("/clients/me/contracts", params={"closed": False, "open": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_closed(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and c.returnedDate is not None]
        response = test_client.get("/clients/me/contracts", params={"expired": False, "open": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_closed_and_open(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and (c.endDate >= datetime.utcnow().date() or c.returnedDate is not None)]
        response = test_client.get("/clients/me/contracts", params={"expired": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_closed_and_expired(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and (c.returnedDate is not None or (c.returnedDate is None and c.endDate < datetime.utcnow().date()))]
        response = test_client.get("/clients/me/contracts", params={"open": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_open_and_expired(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = [c for c in contracts if c.clientId == client.id and c.returnedDate is None]
        response = test_client.get("/clients/me/contracts", params={"closed": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contracts_none(clients, contracts, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        expected_contracts = []
        response = test_client.get("/clients/me/contracts", params={"expired": False, "open": False, "closed": False}, headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(expected_contracts)
        assert all([contract in expected_contracts for contract in response_json])


def test_get_my_contract(contracts, clients, client_auth_headers):
    for client, client_auth_header in zip(clients, client_auth_headers):
        client_contracts = [c for c in contracts if c.clientId == client.id]
        for client_contract in client_contracts:
            response = test_client.get("/clients/me/contracts/{contractId}".format(contractId=client_contract.id), headers=client_auth_header)

            assert response.status_code == 200
            response_json = response.json()

            assert response_json.get("workingUsername") == client_contract.workingUser.username
            assert response_json.get("checkingUsername") == client_contract.checkingUser.username
            assert response_json.get("depositCollectingUsername") == client_contract.depositCollectingUser.username

            if client_contract.returnedDate is not None:
                assert response_json.get("returnAcceptingUsername") == client_contract.returnAcceptingUser.username
                assert response_json.get("depositReturningUsername") == client_contract.depositReturningUser.username
                assert response_json.get("returnedDate") == str(client_contract.returnedDate)
            else:
                assert response_json.get("returnAcceptingUsername") is None
                assert response_json.get("depositReturningUsername") is None
                assert response_json.get("returnedDate") is None

            assert response_json.get("id") == str(client_contract.id)
            assert response_json.get("startDate") == str(client_contract.startDate)
            assert response_json.get("endDate") == str(client_contract.endDate)

            assert response_json.get("depositAmountReturned") == client_contract.depositAmountReturned
            assert response_json.get("detailsSent") == client_contract.detailsSent
            assert response_json.get("expiryReminderSent") == client_contract.expiryReminderSent
            assert response_json.get("returnDetailsSent") == client_contract.returnDetailsSent
            assert response_json.get("clientId") == str(client_contract.clientId)
            assert response_json.get("bikeId") == str(client_contract.bikeId)
            assert response_json.get("depositAmountCollected") == client_contract.depositAmountCollected
            assert response_json.get("conditionOfBike") == client_contract.conditionOfBike
            assert response_json.get("contractType") == client_contract.contractType
            assert response_json.get("notes") == client_contract.notes


def test_get_my_appointments(clients, client_auth_headers, appointments):
    for client, client_auth_header in zip(clients, client_auth_headers):
        client_appointments = [a for a in appointments if a.clientId == client.id]
        response = test_client.get("/clients/me/appointments", headers=client_auth_header)

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == len(client_appointments)
        assert all([a in client_appointments for a in response_json])


def test_cancel_my_appointment(clients, client_auth_headers, appointments):
    for client, client_auth_header in zip(clients, client_auth_headers):
        client_appointments = [a for a in appointments if a.clientId == client.id]
        for appointment in client_appointments:
            response = test_client.patch("/clients/me/appointments/{appointmentId}/cancel".format(appointmentId=appointment.id), headers=client_auth_header)

            assert response.status_code == 200

            db.refresh(appointment)
            assert response.json() == appointment
            assert response.json().get("cancelled")


def test_get_client(clients, normal_user_auth_header):
    for client in clients:
        response = test_client.get("/clients/{clientId}".format(clientId=client.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == client


def test_update_client_full(clients, normal_user_auth_header):
    for client in clients:
        new_details = {
            "firstName": client.firstName + "thisIsNew",
            "lastName": client.lastName + "thisAlso",
            "emailAddress": "New.Email.Address@example.com"
        }
        response = test_client.patch("/clients/{clientId}".format(clientId=client.id), json=new_details, headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() != client
        assert response.json().get("firstName") == new_details["firstName"].lower()
        assert response.json().get("lastName") == new_details["lastName"].lower()
        assert response.json().get("emailAddress") == new_details["emailAddress"].lower()

        db.refresh(client)

        assert response.json() == client


def test_get_client_contracts_all(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_open(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and c.endDate >= datetime.utcnow().date() and c.returnedDate is None]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"expired": False, "closed": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_closed(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and c.returnedDate is not None]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"open": False, "expired": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_expired(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and c.endDate < datetime.utcnow().date() and c.returnedDate is None]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"open": False, "closed": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_open_and_closed(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and (c.endDate >= datetime.utcnow().date() or c.returnedDate is not None)]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"expired": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_open_and_expired(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and c.returnedDate is None]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"closed": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_closed_and_expired(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id and (c.returnedDate is not None or (c.returnedDate is None and c.endDate < datetime.utcnow().date()))]

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"open": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_contracts_none(clients, normal_user_auth_header, contracts):
    for client in clients:
        client_contracts = []

        response = test_client.get("/clients/{clientId}/contracts".format(clientId=client.id), params={"open": False, "expired": False, "closed": False}, headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_contracts)
        assert all([c in client_contracts for c in response_json])


def test_get_client_appointments(clients, normal_user_auth_header, appointments):
    for client in clients:
        client_appointments = [a for a in appointments if a.clientId == client.id]

        response = test_client.get("/clients/{clientId}/appointments".format(clientId=client.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == len(client_appointments)
        assert all([a in client_appointments for a in response_json])
