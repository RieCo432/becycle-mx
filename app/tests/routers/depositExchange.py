from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
import datetime

test_client = TestClient(app)


def test_create_deposit_exchange_between_users(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[0]
    to_user = users[2]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 200

    added_deposit_exchange = db.scalar(
        select(models.DepositExchange)
        .where(
            (models.DepositExchange.fromUserId == from_user.id)
            & (models.DepositExchange.toUserId == to_user.id)
            & (models.DepositExchange.amount == 20)
            & (models.DepositExchange.date == datetime.datetime.utcnow().date())
        )
    )

    assert response.json() == added_deposit_exchange


def test_create_deposit_exchange_to_bank(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[0]
    to_user = users[6]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username.lower()}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 200

    added_deposit_exchange = db.scalar(
        select(models.DepositExchange)
        .where(
            (models.DepositExchange.fromUserId == from_user.id)
            & (models.DepositExchange.toUserId == to_user.id)
            & (models.DepositExchange.amount == 20)
            & (models.DepositExchange.date == datetime.datetime.utcnow().date())
        )
    )

    assert response.json() == added_deposit_exchange


def test_create_deposit_exchange_from_bank(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[6]
    to_user = users[0]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username.lower()}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 200

    added_deposit_exchange = db.scalar(
        select(models.DepositExchange)
        .where(
            (models.DepositExchange.fromUserId == from_user.id)
            & (models.DepositExchange.toUserId == to_user.id)
            & (models.DepositExchange.amount == 20)
            & (models.DepositExchange.date == datetime.datetime.utcnow().date())
        )
    )

    assert response.json() == added_deposit_exchange


def test_create_deposit_exchange_same_user(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[0]
    to_user = users[0]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "To and From cannot be the same!"


def test_create_deposit_from_bank_not_treasurer(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[6]
    to_user = users[2]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username.lower()}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "Only Treasurer can transfer deposits to the BANK"


def test_create_deposit_to_bank_not_treasurer(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[2]
    to_user = users[6]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 20,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username.lower()}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "Only Treasurer can transfer deposits to the BANK"


def test_create_deposit_exchange_insufficient_balance(users, normal_user_auth_header, contracts, deposit_exchanges):
    from_user = users[0]
    to_user = users[2]

    response = test_client.post("/deposit-exchanges", json={
        "amount": 2000,
        "deposit_returning_username": from_user.username,
        "deposit_returning_user_password": f"{from_user.username}1234",
        "deposit_receiving_username": to_user.username,
        "deposit_receiving_user_password": f"{to_user.username}1234"
    }, headers=normal_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "From User does not have enough funds!"


def test_get_deposit_exchange_users(users, normal_user_auth_header):
    response = test_client.get("/deposit-exchanges/users", headers=normal_user_auth_header)
    expected_users = [u for u in users if u.treasurer or u.depositBearer or u.username == "BANK"]

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len(expected_users)
    assert all([u in expected_users for u in response_json])