from uuid import uuid4

from app.tests.pytestFixtures import *
from app.dependencies import *
from app.auth import create_expired_access_token, create_access_token
from fastapi import HTTPException, status


@pytest.mark.asyncio
async def test_get_current_user(users, user_auth_tokens):
    for i, token in enumerate(user_auth_tokens):
        auth_user = await get_current_user(token=token.access_token, db=db)

        assert auth_user == users[i]


@pytest.mark.asyncio
async def test_get_current_user_expired(users):
    for i, user in enumerate(users):
        expired_token = create_expired_access_token(data={"sub": str(user.username)})
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(token=expired_token, db=db)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_user_username_none():
    token = create_access_token(data={})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token, db=db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_user_username_does_not_exist():
    token = create_access_token(data={"sub": "noWay"})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token, db=db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_client(clients, client_auth_tokens):
    for i, token in enumerate(client_auth_tokens):
        auth_client = await get_current_client(token=token.access_token, db=db)

        assert auth_client == clients[i]


@pytest.mark.asyncio
async def test_get_current_client_expired(clients):
    for i, client in enumerate(clients):
        expired_token = create_expired_access_token(data={"sub": str(client.id)})
        with pytest.raises(HTTPException) as excinfo:
            await get_current_client(token=expired_token, db=db)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_client_id_none():
    token = create_access_token(data={})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_client(token=token, db=db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_user_client_does_not_exist():
    token = create_access_token(data={"sub": str(uuid4())})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_client(token=token, db=db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail.get("description") == "Could not validate credentials. Please login again."


@pytest.mark.asyncio
async def test_get_current_active_user(users):
    auth_user = await get_current_active_user(users[0])

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_current_active_user_soft_deleted(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_current_active_user(users[4])

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Soft-deleted User"


@pytest.mark.asyncio
async def test_get_current_appointment_manager_user(users):
    auth_user = await get_current_appointment_manager_user(users[0])

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_current_appointment_manager_user_not(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_current_appointment_manager_user(users[2])

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail.get("description") == "Appointment manager privileges are required for this action!"


@pytest.mark.asyncio
async def test_get_working_user_password(users):
    auth_user = await get_working_user(
        working_username=users[0].username,
        working_user_password_or_pin=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_working_user_pin(users):
    auth_user = await get_working_user(
        working_username=users[0].username,
        working_user_password_or_pin="0000",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_working_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_working_user(
            working_username=users[0].username,
            working_user_password_or_pin="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Working User wrong password or pin"


@pytest.mark.asyncio
async def test_get_working_user_wrong_pin(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_working_user(
            working_username=users[0].username,
            working_user_password_or_pin="1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Working User wrong password or pin"


@pytest.mark.asyncio
async def test_get_checking_user_password(users):
    auth_user = await get_checking_user(
        checking_username=users[0].username,
        checking_user_password_or_pin=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_checking_user_pin(users):
    auth_user = await get_checking_user(
        checking_username=users[0].username,
        checking_user_password_or_pin="0000",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_checking_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_checking_user(
            checking_username=users[0].username,
            checking_user_password_or_pin="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Checking User wrong password or pin"


@pytest.mark.asyncio
async def test_get_checking_user_wrong_pin(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_checking_user(
            checking_username=users[0].username,
            checking_user_password_or_pin="1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Checking User wrong password or pin"


@pytest.mark.asyncio
async def test_get_checking_user_not_a_rental_checker(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_checking_user(
            checking_username=users[2].username,
            checking_user_password_or_pin="2222",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Not a rental checker!"


@pytest.mark.asyncio
async def test_get_deposit_receiving_user_password(users):
    auth_user = await get_deposit_receiving_user(
        deposit_receiving_username=users[0].username,
        deposit_receiving_user_password=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_deposit_receiving_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_receiving_user(
            deposit_receiving_username=users[0].username,
            deposit_receiving_user_password="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Deposit receiving user wrong password"


@pytest.mark.asyncio
async def test_get_deposit_receiving_user_not_a_deposit_bearer(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_receiving_user(
            deposit_receiving_username=users[1].username,
            deposit_receiving_user_password=f"{users[1].username}1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Not a deposit bearer!"


@pytest.mark.asyncio
async def test_get_deposit_returning_user_password(users):
    auth_user = await get_deposit_returning_user(
        deposit_returning_username=users[0].username,
        deposit_returning_user_password=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_deposit_returning_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_returning_user(
            deposit_returning_username=users[0].username,
            deposit_returning_user_password="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Deposit returning user wrong password"


@pytest.mark.asyncio
async def test_get_deposit_returning_user_not_a_deposit_bearer(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_returning_user(
            deposit_returning_username=users[1].username,
            deposit_returning_user_password=f"{users[1].username}1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Not a deposit bearer!"


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user(users):
    auth_user = await get_deposit_exchange_to_user(
        deposit_receiving_username=users[0].username,
        deposit_receiving_user_password=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_exchange_to_user(
            deposit_receiving_username=users[0].username,
            deposit_receiving_user_password="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Deposit receiving user wrong password"


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user_deposit_bearer(users):
    auth_user = await get_deposit_exchange_to_user(
        deposit_receiving_username=users[2].username,
        deposit_receiving_user_password=f"{users[2].username}1234",
        db=db
    )

    assert auth_user == users[2]


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user_treasurer(users):
    auth_user = await get_deposit_exchange_to_user(
        deposit_receiving_username=users[5].username,
        deposit_receiving_user_password=f"{users[5].username}1234",
        db=db
    )

    assert auth_user == users[5]


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user_bank(users):
    auth_user = await get_deposit_exchange_to_user(
        deposit_receiving_username="BANK",
        deposit_receiving_user_password="bank1234",
        db=db
    )

    assert auth_user == users[6]


@pytest.mark.asyncio
async def test_get_deposit_exchange_to_user_not_allowed(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_exchange_to_user(
            deposit_receiving_username=users[3].username,
            deposit_receiving_user_password=f"{users[3].username}1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Not a deposit bearer, treasurer or BANK!"


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user(users):
    auth_user = await get_deposit_exchange_from_user(
        deposit_returning_username=users[0].username,
        deposit_returning_user_password=f"{users[0].username}1234",
        db=db
    )

    assert auth_user == users[0]


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user_wrong_password(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_exchange_from_user(
            deposit_returning_username=users[0].username,
            deposit_returning_user_password="password1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Deposit returning user wrong password"


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user_deposit_bearer(users):
    auth_user = await get_deposit_exchange_from_user(
        deposit_returning_username=users[2].username,
        deposit_returning_user_password=f"{users[2].username}1234",
        db=db
    )

    assert auth_user == users[2]


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user_treasurer(users):
    auth_user = await get_deposit_exchange_from_user(
        deposit_returning_username=users[5].username,
        deposit_returning_user_password=f"{users[5].username}1234",
        db=db
    )

    assert auth_user == users[5]


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user_bank(users):
    auth_user = await get_deposit_exchange_from_user(
        deposit_returning_username="BANK",
        deposit_returning_user_password="bank1234",
        db=db
    )

    assert auth_user == users[6]


@pytest.mark.asyncio
async def test_get_deposit_exchange_from_user_not_allowed(users):
    with pytest.raises(HTTPException) as excinfo:
        await get_deposit_exchange_from_user(
            deposit_returning_username=users[3].username,
            deposit_returning_user_password=f"{users[3].username}1234",
            db=db
        )

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail.get("description") == "Not a deposit bearer, treasurer or BANK!"
