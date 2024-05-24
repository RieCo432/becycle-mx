from sqlalchemy import select, func

from app.tests.pytestFixtures import *
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

test_client = TestClient(app)


def test_get_contract(contracts, normal_user_auth_header):
    for contract in contracts:
        response = test_client.get("/contracts/{contractId}/".format(contractId=contract.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == contract


def test_get_contracts_all(contracts, normal_user_auth_header):
    response = test_client.get("/contracts", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(contracts)
    assert all([contract in contracts for contract in response_json])


def test_get_contracts_open(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if c.endDate >= datetime.utcnow().date() and c.returnedDate is None]
    response = test_client.get("/contracts", params={"closed": False, "expired": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_expired(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if c.endDate < datetime.utcnow().date() and c.returnedDate is None]
    response = test_client.get("/contracts", params={"closed": False, "open": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_closed(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if c.returnedDate is not None]
    response = test_client.get("/contracts", params={"expired": False, "open": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_closed_and_open(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if (c.endDate >= datetime.utcnow().date() or c.returnedDate is not None)]
    response = test_client.get("/contracts", params={"expired": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_closed_and_expired(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if (c.returnedDate is not None or (c.returnedDate is None and c.endDate < datetime.utcnow().date()))]
    response = test_client.get("/contracts", params={"open": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_open_and_expired(contracts, normal_user_auth_header):
    expected_contracts = [c for c in contracts if c.returnedDate is None]
    response = test_client.get("/contracts", params={"closed": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_get_contracts_none(contracts, normal_user_auth_header):
    expected_contracts = []
    response = test_client.get("/contracts", params={"expired": False, "open": False, "closed": False}, headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == len(expected_contracts)
    assert all([contract in expected_contracts for contract in response_json])


def test_create_contract(contracts, normal_user_auth_header, users, bikes, clients):
    contract_data = {
        "clientId": str(clients[1].id),
        "bikeId": str(bikes[2].id),
        "depositAmountCollected": 40,
        "conditionOfBike": "fair",
        "contractType": "standard",
        "notes": "test create contract"
    }

    request_json = {
        "contract_data": contract_data,
        "working_username": users[2].username,
        "working_user_password_or_pin": "2222",
        "checking_username": users[1].username,
        "checking_user_password_or_pin": f"{users[1].username}1234",
        "deposit_receiving_username": users[0].username,
        "deposit_receiving_user_password": f"{users[0].username}1234",

    }

    assert db.scalar(
        select(models.Contract)
        .where(models.Contract.notes == "test create contract")
    ) is None

    response = test_client.post("/contract", json=request_json, headers=normal_user_auth_header)

    assert response.status_code == 200

    new_contract = db.scalar(
        select(models.Contract)
        .where(models.Contract.notes == "test create contract")
    )

    assert response.json() == new_contract
    assert new_contract.startDate == datetime.utcnow().date()
    assert new_contract.endDate == datetime.utcnow().date() + relativedelta(months=6)


def test_create_contract_working_and_checking_user_equal(contracts, normal_user_auth_header, users, bikes, clients):
    contract_data = {
        "clientId": str(clients[1].id),
        "bikeId": str(bikes[2].id),
        "depositAmountCollected": 40,
        "conditionOfBike": "fair",
        "contractType": "standard",
        "notes": "test create contract"
    }

    request_json = {
        "contract_data": contract_data,
        "working_username": users[1].username,
        "working_user_password_or_pin": "1111",
        "checking_username": users[1].username,
        "checking_user_password_or_pin": f"{users[1].username}1234",
        "deposit_receiving_username": users[0].username,
        "deposit_receiving_user_password": f"{users[0].username}1234",

    }

    assert db.scalar(
        select(models.Contract)
        .where(models.Contract.notes == "test create contract")
    ) is None

    response = test_client.post("/contract", json=request_json, headers=normal_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Working and checking volunteer cannot be the same!"


def test_delete_contract(contracts, paper_contracts, admin_user_auth_header):
    number_of_contracts = len(contracts)
    contract_id_to_delete = contracts[1].id

    response = test_client.delete("/contracts/{contractId}".format(contractId=contract_id_to_delete), headers=admin_user_auth_header)

    assert response.status_code == 200

    number_of_contracts_remaining = db.scalar(
        select(func.count(models.Contract.id))
    )
    assert number_of_contracts_remaining == number_of_contracts - 1
    assert db.scalar(
        select(models.Contract)
        .where(models.Contract.id == contract_id_to_delete)
    ) is None


def test_patch_contract(contracts, users, admin_user_auth_header):
    patch_data = {
        "depositAmountCollected": 25,
        "conditionOfBike": "excellent",
        "notes": "patched",
        "contractType": "kids",
        "startDate": (datetime.utcnow().date() - relativedelta(months=10)).strftime("%Y-%m-%d"),
        "endDate": (datetime.utcnow().date() + relativedelta(months=2)).strftime("%Y-%m-%d"),
        "workingUserId": str(users[0].id),
        "checkingUserId": str(users[1].id),
        "depositCollectingUserId": str(users[0].id),
        "returned": False
    }

    response = test_client.patch("/contracts/{contractId}".format(contractId=contracts[2].id), json=patch_data, headers=admin_user_auth_header)

    assert response.status_code == 200

    assert response.json() != contracts[2]

    db.refresh(contracts[2])

    assert response.json() == contracts[2]

    assert contracts[2].depositAmountCollected == 25
    assert contracts[2].conditionOfBike == "excellent"
    assert contracts[2].notes == "patched"
    assert contracts[2].contractType == "kids"
    assert contracts[2].startDate == datetime.utcnow().date() - relativedelta(months=10)
    assert contracts[2].endDate == datetime.utcnow().date() + relativedelta(months=2)
    assert contracts[2].workingUserId == users[0].id
    assert contracts[2].checkingUserId == users[1].id
    assert contracts[2].depositCollectingUserId == users[0].id


def test_return_bike_insufficient_funds(contracts, users, normal_user_auth_header):
    request_json = {
        "working_username": users[1].username,
        "working_user_password_or_pin": "1111",
        "deposit_returning_username": users[0].username,
        "deposit_returning_user_password": f"{users[0].username}1234",
        "deposit_amount_returned": 30,
    }

    response = test_client.patch("/contracts/{contractId}/return".format(contractId=contracts[2].id), json=request_json, headers=normal_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "This deposit bearer does not have enough funds!"


def test_return_bike(contracts, users, normal_user_auth_header):
    request_json = {
        "working_username": users[1].username,
        "working_user_password_or_pin": "1111",
        "deposit_returning_username": users[2].username,
        "deposit_returning_user_password": f"{users[2].username}1234",
        "deposit_amount_returned": 30,
    }

    response = test_client.patch("/contracts/{contractId}/return".format(contractId=contracts[2].id), json=request_json, headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() != contracts[2]

    db.refresh(contracts[2])

    assert response.json() == contracts[2]

    assert contracts[2].returnedDate == datetime.utcnow().date()
    assert contracts[2].depositAmountReturned == 30
    assert contracts[2].depositReturningUserId == users[2].id
    assert contracts[2].returnAcceptingUserId == users[1].id


def test_return_bike_deposit_returned_too_high(contracts, users, normal_user_auth_header):
    request_json = {
        "working_username": users[1].username,
        "working_user_password_or_pin": "1111",
        "deposit_returning_username": users[2].username,
        "deposit_returning_user_password": f"{users[2].username}1234",
        "deposit_amount_returned": 50,
    }

    response = test_client.patch("/contracts/{contractId}/return".format(contractId=contracts[2].id), json=request_json, headers=normal_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Amount returned is higher than amount collected!"


def test_extend_contract(contracts, normal_user_auth_header):
    response = test_client.patch("/contracts/{contractId}/extend".format(contractId=contracts[2].id), headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() != contracts[2]

    db.refresh(contracts[2])

    assert response.json() == contracts[2]

    assert contracts[2].endDate == datetime.utcnow().date() + relativedelta(months=6)


def test_get_contract_types(contract_types, normal_user_auth_header):
    response = test_client.get("/contract/types", headers=normal_user_auth_header)

    assert response.status_code == 200
    assert len(response.json()) == len(contract_types)
    assert all([ct in contract_types for ct in response.json()])


def test_get_paper_contract(paper_contracts, normal_user_auth_header):
    for paper_contract in paper_contracts:
        response = test_client.get("/contracts/paper", params={"paper_id": paper_contract.id}, headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == str(paper_contract.contractId)


def test_get_paper_contract_suggestions(paper_contracts, normal_user_auth_header):
    queries = ["1234", "lkj", "qrst", None]
    expected_results = [
        [paper_contracts[0].id, paper_contracts[2].id],
        [paper_contracts[1].id],
        [],
        []
    ]

    for query, expected_result in zip(queries, expected_results):
        response = test_client.get("/contracts/paper/suggestions", params={"old_id": query} if query is not None else {}, headers=normal_user_auth_header)

        assert response.status_code == 200
        assert len(response.json()) == len(expected_result)
        assert all([s in expected_result for s in response.json()])
