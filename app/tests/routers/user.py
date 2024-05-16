from fastapi.testclient import TestClient
from app.tests.pytestFixtures import *
from app.main import app
import app.dependencies as dep


client = TestClient(app)

clear_database()


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
