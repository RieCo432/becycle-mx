from fastapi.testclient import TestClient
from app.tests.pytestFixtures import *
from app.main import app


client = TestClient(app)


def test_get_opening_times(appointment_concurrency_limits, appointment_general_settings):
    response = client.get("/public/opening-times")
    assert response.status_code == 200
    assert response.json() == [
        {"day": "Monday", "open": "16:15", "close": "19:45"},
        {"day": "Wednesday", "open": "16:15", "close": "19:45"}
    ]


def test_get_opening_days(appointment_general_settings):
    response = client.get("/public/opening-days")
    assert response.status_code == 200
    assert response.json() == [0, 2]


def test_get_opening_hours(appointment_concurrency_limits):
    response = client.get("/public/opening-hours")
    assert response.status_code == 200
    assert response.json() == {"open_time": "16:15:00", "close_time": "19:45:00"}


def test_get_slot_duration(appointment_general_settings):
    response = client.get("/public/slot-duration")
    assert response.status_code == 200
    assert response.json() == 15


def test_get_next_closed_day(closed_days):
    response = client.get("/public/next-closed-day")

    next_closed_date = str(datetime.datetime.utcnow().date() + relativedelta(days=7))

    assert response.status_code == 200
    assert response.json() == {"date": next_closed_date, "note": "Workshop Day"}


def test_get_address(address):
    response = client.get("/public/address")
    assert response.status_code == 200
    assert response.json() == {"number": "21-23", "street": "High Street", "postcode": "AB24 3EE", "city": "Aberdeen"}


def test_get_user_presentation_cards(user_presentation_cards):
    response = client.get("/public/users/presentation-cards")
    assert response.status_code == 200
    assert all(
        [
            response_card == {
                "bio": user_presentation_card.bio,
                "id": str(user_presentation_card.id),
                "name": user_presentation_card.name,
                "photoContentType": user_presentation_card.photoContentType
            } for response_card, user_presentation_card in zip(
                response.json(),
                [user_presentation_card for user_presentation_card in user_presentation_cards if
                    not user_presentation_card.user.softDeleted]
            )
        ])


def test_get_user_presentation_card_photo(user_photos, user_presentation_cards):
    for user_presentation_card, user_photo in zip(user_presentation_cards, user_photos):
        response = client.get("/public/users/presentation-cards/{cardId}/photo".format(cardId=user_presentation_card.id))

        assert response.status_code == 200
        assert response.content == user_photo.content