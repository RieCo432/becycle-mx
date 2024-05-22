from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
import datetime

test_client = TestClient(app)


# @deposit_exchanges.post("/deposit-exchanges", dependencies=[Depends(dep.get_current_active_user)])
# async def create_deposit_exchange(
#         amount: Annotated[int, Body()],
#         from_user: models.User = Depends(dep.get_deposit_exchange_from_user),
#         to_user: models.User = Depends(dep.get_deposit_exchange_to_user),
#         db: Session = Depends(dep.get_db)) -> schemas.DepositExchange:
#
#     if to_user.id == from_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail={"description": "To and From cannot be the same!"},
#             headers={"WWW-Authenticate": "Bearer"}
#         )
#
#     if (
#             (to_user.username == 'BANK' and not from_user.treasurer)
#             or (from_user.username == 'BANK' and not to_user.treasurer)
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail={"description": "Only Treasurer can transfer deposits to the BANK"}
#         )
#
#     if amount > from_user.get_deposit_bearer_balance():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail={"description": "From User does not have enough funds!"},
#             headers={"WWW-Authenticate": "Bearer"}
#         )
#
#     return crud.create_deposit_exchange(db=db, amount=amount, from_user_id=from_user.id, to_user_id=to_user.id)
#

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

#
# @deposit_exchanges.get("/deposit-exchanges", dependencies=[Depends(dep.get_current_active_user)])
# async def get_deposit_exchanges(db: Session = Depends(dep.get_db)) -> list[schemas.DepositExchange]:
#     return crud.get_deposit_exchanges(db=db)
#
#
# @deposit_exchanges.get("/deposit-exchanges/users", dependencies=[Depends(dep.get_current_active_user)])
# async def get_deposit_exchange_users(db: Session = Depends(dep.get_db)) -> list[schemas.User]:
#     return crud.get_deposit_exchange_users(db=db)