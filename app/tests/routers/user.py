from fastapi.testclient import TestClient
from app.tests.pytestFixtures import *
from app.main import app
import app.crud as crud
from sqlalchemy import select
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
        assert response.json().get("detail").get(
            "description") == "Cannot login with default password. Please contact an admin to set a password!"


def test_get_user_me(users, user_auth_tokens):
    for user, user_auth_token in zip(users, user_auth_tokens):
        response = client.get("/users/me", headers={"Authorization": 'Bearer ' + user_auth_token.access_token})

        if not user.softDeleted:
            assert response.status_code == 200
            assert response.json() == user
        else:
            assert response.status_code == 400
            assert response.json().get("detail").get("description") == "Soft-deleted User"


def test_get_users(users, normal_user_auth_header):
    response = client.get("/users", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len(users)
    assert all(response_user in users for response_user in response_json)


def test_get_user(users, normal_user_auth_header):
    for user in users:
        response = client.get("/users/{userId}".format(userId=user.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == user


def test_patch_user_not_admin(users, normal_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[1].id), json={
        "passwordCleartext": "NewPassword",
        "treasurer": True,
    }, headers=normal_user_auth_header)

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "Admin privileges are required for this action!"


def test_patch_user_own_role(users, admin_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[0].id), json={
        "treasurer": False,
    }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "You cannot modify your own roles!"


def test_patch_user_soft_deleted(users, admin_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[4].id), json={
        "treasurer": True,
    }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "User is soft-deleted"


def test_patch_user_role_change(users, admin_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[1].id), json={
        "treasurer": True,
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    assert response.json() != users[1]
    db.refresh(users[1])
    assert response.json() == users[1]


def test_patch_user_all_roles_change(users, admin_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[3].id), json={
        "admin": True,
        "depositBearer": True,
        "rentalChecker": True,
        "appointmentManager": True,
        "treasurer": True,
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    assert response.json() != users[3]
    db.refresh(users[3])
    assert response.json() == users[3]


def test_patch_user_soft_delete(users, admin_user_auth_header):
    response = client.patch("/users/{userId}".format(userId=users[3].id), json={
        "softDeleted": True
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    assert response.json() != users[3]
    db.refresh(users[3])
    assert response.json() == users[3]


def test_patch_user_password_change(users, admin_user_auth_header):
    # verify old password is valid and new password is not
    assert crud.authenticate_user(users[1].username, f"{users[1].username}1234", db=db)
    assert not crud.authenticate_user(users[1].username, "NewPassword", db=db)

    response = client.patch("/users/{userId}".format(userId=users[1].id), json={
        "passwordCleartext": "NewPassword",
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    old_password = users[1].password
    db.refresh(users[1])
    assert old_password != users[1].password

    # verify old password is not valid, but new password is
    assert not crud.authenticate_user(users[1].username, f"{users[1].username}1234", db=db)
    assert crud.authenticate_user(users[1].username, "NewPassword", db=db)


def test_patch_user_pin_change(users, admin_user_auth_header):
    # verify old pin is valid and new password is not
    assert crud.validate_user_signature(users[1].username, "1111", db=db)
    assert not crud.validate_user_signature(users[1].username, "1234", db=db)

    response = client.patch("/users/{userId}".format(userId=users[1].id), json={
        "pinCleartext": "1234",
    }, headers=admin_user_auth_header)

    assert response.status_code == 200

    old_pin = users[1].pin
    db.refresh(users[1])
    assert old_pin != users[1].pin

    # verify old pin is not valid, but new password is
    assert not crud.validate_user_signature(users[1].username, "1111", db=db)
    assert crud.validate_user_signature(users[1].username, "1234", db=db)


def test_get_my_deposit_balance_normal_user(users, normal_user_auth_header):
    response = client.get("/users/me/deposit_balance", headers=normal_user_auth_header)

    assert response.status_code == 403
    assert response.json().get("detail").get("description") == "This page can only be viewed by deposit bearers!"


def test_get_my_deposit_balance(users, deposit_bearer_user_auth_header):
    response = client.get("/users/me/deposit_balance", headers=deposit_bearer_user_auth_header)

    assert response.status_code == 200
    assert (response.json() == sum([contract.depositAmountCollected for contract in users[2].depositCollectedContracts])
            - sum([contract.depositAmountReturned for contract in users[2].depositReturnedContracts])
            + sum([deposit_exchange.amount for deposit_exchange in users[2].depositExchangesReceived])
            - sum([deposit_exchange.amount for deposit_exchange in users[2].depositExchangesGiven]))


def test_post_user_password_check_wrong(users):
    for user in users:
        response = client.post("/user/check/password", data={
            "username": user.username,
            "password": f"{user.username}12"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200
        assert not response.json()


def test_post_user_password_check_nonexistent_user(users):
    response = client.post("/user/check/password", data={
        "username": "doesnotexist",
        "password": "doesntmatter"
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    assert response.status_code == 200
    assert not response.json()


def test_post_user_password_check(users):
    for user in users:
        response = client.post("/user/check/password", data={
            "username": user.username,
            "password": f"{user.username}1234"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200
        assert response.json()


def test_post_user_password_or_pin_check_wrong_password(users):
    for user in users:
        response = client.post("/user/check/password-or-pin", data={
            "username": user.username,
            "password": f"{user.username}12"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200
        assert not response.json()


def test_post_user_password_or_pin_check_nonexistent_user(users):
    response = client.post("/user/check/password-or-pin", data={
        "username": "doesnotexist",
        "password": "doesntmatter"
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    assert response.status_code == 200
    assert not response.json()


def test_post_user_password_or_pin_check_correct_password(users):
    for user in users:
        response = client.post("/user/check/password-or-pin", data={
            "username": user.username,
            "password": f"{user.username}1234"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200
        assert response.json()


def test_post_user_password_or_pin_check_wrong_pin(users):
    for user in users:
        response = client.post("/user/check/password-or-pin", data={
            "username": user.username,
            "password": "1234"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200
        assert not response.json()


def test_post_user_password_or_pin_check_correct_pin(users):
    for i, user in enumerate(users):
        response = client.post("/user/check/password-or-pin", data={
            "username": user.username,
            "password": f"{i}{i}{i}{i}"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

        assert response.status_code == 200

        if user.pin is not None:
            assert response.json()
        else:
            assert not response.json()


def test_create_user_no_pin_no_roles(users, admin_user_auth_header):
    new_user_json = {
        "username": "newUser",
        "password_cleartext": "newPassword"
    }

    response = client.post("/user", json=new_user_json, headers=admin_user_auth_header)

    assert response.status_code == 200

    new_user = db.scalar(
        select(models.User)
        .where(models.User.username == new_user_json["username"])
    )

    assert response.json() == new_user
    assert new_user.pin is None
    assert not new_user.admin
    assert not new_user.depositBearer
    assert not new_user.rentalChecker
    assert not new_user.treasurer
    assert not new_user.appointmentManager
    assert not new_user.softDeleted

    assert crud.authenticate_user(new_user_json["username"], new_user_json["password_cleartext"], db=db)


def test_create_user_with_pin_and_all_roles(users, admin_user_auth_header):
    new_user_json = {
        "username": "newUser",
        "password_cleartext": "newPassword",
        "pin_cleartext": "1234",
        "admin": True,
        "depositBearer": True,
        "rentalChecker": True,
        "appointmentManager": True,
        "treasurer": True
    }

    response = client.post("/user", json=new_user_json, headers=admin_user_auth_header)

    assert response.status_code == 200

    new_user = db.scalar(
        select(models.User)
        .where(models.User.username == new_user_json["username"])
    )

    assert response.json() == new_user
    assert new_user.pin is not None
    assert new_user.admin
    assert new_user.depositBearer
    assert new_user.rentalChecker
    assert new_user.treasurer
    assert new_user.appointmentManager
    assert not new_user.softDeleted

    assert crud.authenticate_user(new_user_json["username"], new_user_json["password_cleartext"], db=db)
    assert crud.validate_user_signature(new_user_json["username"], new_user_json["pin_cleartext"], db=db)


def test_create_user_already_exists(users, admin_user_auth_header):
    new_user_json = {
        "username": users[3].username,
        "password_cleartext": "newPassword"
    }

    response = client.post("/user", json=new_user_json, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Integrity Error: Does this user already exist?"


def test_get_active_users(users, normal_user_auth_header):
    response = client.get("/users/active-users", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len([user for user in users if not user.softDeleted])
    assert all([response_user in [user for user in users if not user.softDeleted] for response_user in response_json])


def test_get_deposit_bearer_users(users, normal_user_auth_header):
    response = client.get("/users/deposit-bearers", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len([user for user in users if user.depositBearer])
    assert all([response_user in [user for user in users if user.depositBearer] for response_user in response_json])


def test_get_rental_checkers(users, normal_user_auth_header):
    response = client.get("/users/rental-checkers", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len([user for user in users if user.rentalChecker])
    assert all([response_user in [user for user in users if user.rentalChecker] for response_user in response_json])


def test_update_presentation_card_no_photo(user_presentation_cards, admin_user_auth_header):
    new_card_details_json = {
        "name": "New Name",
        "bio": "This is a new bio",
    }

    response = client.post("/users/presentation-card/{cardId}".format(cardId=user_presentation_cards[1].id),
                           data=new_card_details_json,
                           headers=admin_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json != user_presentation_cards[1]
    db.refresh(user_presentation_cards[1])
    assert response_json == user_presentation_cards[1]
    assert response_json.get("name") == new_card_details_json.get("name")
    assert response_json.get("bio") == new_card_details_json.get("bio")


def test_update_presentation_card(user_presentation_cards, admin_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "new_freddy.jpg")
    with open(photo_filepath, "rb") as photo_file:
        new_card_details_json = {
            "name": "New Name",
            "bio": "This is a new bio",
        }

        response = client.post("/users/presentation-card/{cardId}".format(cardId=user_presentation_cards[1].id),
                               data=new_card_details_json,
                               files={"photo": ("new_freddy.jpg", photo_file, "image/jpeg")},
                               headers=admin_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    old_photo_file_id = user_presentation_cards[1].photoFileId

    assert response_json != user_presentation_cards[1]
    db.refresh(user_presentation_cards[1])
    assert response_json == user_presentation_cards[1]
    assert response_json.get("name") == new_card_details_json.get("name")
    assert response_json.get("bio") == new_card_details_json.get("bio")
    assert user_presentation_cards[1].photoFileId != old_photo_file_id

    old_photo = db.scalar(
        select(models.UserPhoto)
        .where(models.UserPhoto.id == old_photo_file_id)
    )

    assert old_photo is None


def test_update_presentation_card_big_rect_photo(user_presentation_cards, admin_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "new_big_rect_freddy.jpg")
    with open(photo_filepath, "rb") as photo_file:
        new_card_details_json = {
            "name": "New Name",
            "bio": "This is a new bio",
        }

        response = client.post("/users/presentation-card/{cardId}".format(cardId=user_presentation_cards[1].id),
                               data=new_card_details_json,
                               files={"photo": ("new_freddy.jpg", photo_file, "image/jpeg")},
                               headers=admin_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    old_photo_file_id = user_presentation_cards[1].photoFileId

    assert response_json != user_presentation_cards[1]
    db.refresh(user_presentation_cards[1])
    assert response_json == user_presentation_cards[1]
    assert response_json.get("name") == new_card_details_json.get("name")
    assert response_json.get("bio") == new_card_details_json.get("bio")
    assert user_presentation_cards[1].photoFileId != old_photo_file_id

    old_photo = db.scalar(
        select(models.UserPhoto)
        .where(models.UserPhoto.id == old_photo_file_id)
    )

    assert old_photo is None

    photo_filepath_temp = os.path.join(photos_directory, "new_big_rect_freddy_temp.jpg")
    with open(photo_filepath_temp, "wb") as photo_file:
        photo_file.write(user_presentation_cards[1].photoFile.content)

    from PIL import Image

    photo = Image.open(photo_filepath_temp)
    assert photo.size == (1024, 1024)


def test_delete_presentation_card(user_presentation_cards, admin_user_auth_header):
    card_to_be_deleted = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == user_presentation_cards[1].id)
    )

    assert card_to_be_deleted is not None

    response = client.delete("/users/presentation-card/{cardId}".format(cardId=user_presentation_cards[1].id),
                             headers=admin_user_auth_header)

    assert response.status_code == 200

    deleted_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == user_presentation_cards[1].id)
    )

    assert deleted_card is None


def test_update_my_presentation_card_no_photo(user_presentation_cards, normal_user_auth_header):
    new_card_details_json = {
        "name": "New Name",
        "bio": "This is a new bio",
    }

    response = client.post("/users/me/presentation-card",
                           data=new_card_details_json,
                           headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    db.refresh(user_presentation_cards[3])
    assert response_json == user_presentation_cards[3]
    assert response_json.get("name") == new_card_details_json.get("name")
    assert response_json.get("bio") == new_card_details_json.get("bio")


def test_update_my_presentation_card_new_with_photo(user_presentation_cards, users, user_auth_tokens):
    new_card_details_json = {
        "name": "New Name",
        "bio": "This is a new bio",
    }

    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "no_card_user.jpg")
    with open(photo_filepath, "rb") as photo_file:
        response = client.post("/users/me/presentation-card",
                               data=new_card_details_json,
                               files={"photo": ("no_card_user.jpg", photo_file, "image/jpeg")},
                               headers={
                                   "Authorization": "Bearer " + user_auth_tokens[5].access_token
                               })

    assert response.status_code == 200
    response_json = response.json()

    assert response_json.get("name") == new_card_details_json.get("name")
    assert response_json.get("bio") == new_card_details_json.get("bio")

    user_presentation_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.userId == users[5].id)
    )

    assert user_presentation_card is not None
    assert user_presentation_card.photoContentType is not None
    assert user_presentation_card.photoFileId is not None


def test_update_my_presentation_card_new_without_photo(user_presentation_cards, users, user_auth_tokens):
    new_card_details_json = {
        "name": "New Name",
        "bio": "This is a new bio",
    }

    response = client.post("/users/me/presentation-card",
                           data=new_card_details_json,
                           headers={
                               "Authorization": "Bearer " + user_auth_tokens[5].access_token
                           })

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "No photo provided"


def test_delete_my_presentation_card(user_presentation_cards, normal_user_auth_header):
    card_to_be_deleted = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == user_presentation_cards[3].id)
    )

    assert card_to_be_deleted is not None

    response = client.delete("/users/me/presentation-card", headers=normal_user_auth_header)

    assert response.status_code == 200

    deleted_card = db.scalar(
        select(models.UserPresentationCard)
        .where(models.UserPresentationCard.id == user_presentation_cards[3].id)
    )

    assert deleted_card is None


def test_get_my_presentation_card(user_presentation_cards, normal_user_auth_header):
    response = client.get("/users/me/presentation-card", headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() == user_presentation_cards[3]


def test_get_user_presentation_card(user_presentation_cards, users, normal_user_auth_header):
    for user, user_presentation_card in zip(users[:5], user_presentation_cards):
        response = client.get("/users/{userId}/presentation-card".format(userId=user.id),
                              headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.json() == user_presentation_card


def test_get_user_presentation_card_for_user_who_doesnt_have_one(user_presentation_cards, users,
                                                                 normal_user_auth_header):
    response = client.get("/users/{userId}/presentation-card".format(userId=users[5].id),
                          headers=normal_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "User Presentation Card not found"
