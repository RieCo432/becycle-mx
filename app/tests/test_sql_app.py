import datetime

from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient

from app.database.db import Base, engine, SessionLocal
from app.main import app
from app.populate_test_db import populate_test_db


Base.metadata.create_all(bind=engine)

db = SessionLocal()

populate_test_db(db=db)

client = TestClient(app)


'''
Test Public Router
'''


def test_get_opening_times():
    response = client.get("/public/opening-times")
    assert response.status_code == 200
    assert response.json() == [
        {"day": "Monday", "open": "16:15", "close": "19:45"},
        {"day": "Wednesday", "open": "16:15", "close": "19:45"}
    ]


def test_get_opening_days():
    response = client.get("/public/opening-days")
    assert response.status_code == 200
    assert response.json() == [0, 2]


def test_get_opening_hours():
    response = client.get("/public/opening-hours")
    assert response.status_code == 200
    assert response.json() == {"open_time": "16:15:00", "close_time": "19:45:00"}


def test_get_slot_duration():
    response = client.get("/public/slot-duration")
    assert response.status_code == 200
    assert response.json() == 15


def test_get_next_closed_day():
    response = client.get("/public/next-closed-day")

    next_closed_date = str(datetime.datetime.utcnow().date() + relativedelta(days=7))

    assert response.status_code == 200
    assert response.json() == {"date": next_closed_date, "note": "Workshop Day"}


def test_get_address():
    response = client.get("/public/address")
    assert response.status_code == 200
    assert response.json() == {"number": "21-23", "street": "High Street", "postcode": "AB24 3EE", "city": "Aberdeen"}


# def get_user_presentation_cards():

# def get_user_presentation_card_photo():
