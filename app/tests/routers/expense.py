from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
import datetime

test_client = TestClient(app)


def test_post_expense_small_receipt(expenses, expense_types, expense_receipts, normal_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "receipt_test.jpg")
    with open(photo_filepath, "rb") as photo_file:
        new_expense_details = {
            "expense_type": expense_types[0].id,
            "amount": 40,
            "notes": "Some stuff",
            "expense_date": datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
        }

        response = test_client.post("/expenses",
                               data=new_expense_details,
                               files={"receipt_file": ("receipt_test.jpg", photo_file, "image/jpeg")},
                               headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    expense_db = db.scalar(
        select(models.Expense)
        .where(models.Expense.expenseDate == datetime.datetime.utcnow().date())
    )

    assert response_json == expense_db
    assert expense_db.amount == 40.0
    assert expense_db.type == expense_types[0].id
    assert expense_db.notes == "Some stuff"
    assert expense_db.expenseDate == datetime.datetime.utcnow().date()


def test_post_expense_big_receipt_landscape(expenses, expense_types, expense_receipts, normal_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "big_receipt_landscape.jpg")
    with open(photo_filepath, "rb") as photo_file:
        new_expense_details = {
            "expense_type": expense_types[0].id,
            "amount": 40,
            "notes": "Some stuff",
            "expense_date": datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
        }

        response = test_client.post("/expenses",
                               data=new_expense_details,
                               files={"receipt_file": ("big_receipt_landscape.jpg", photo_file, "image/jpeg")},
                               headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    expense_db = db.scalar(
        select(models.Expense)
        .where(models.Expense.expenseDate == datetime.datetime.utcnow().date())
    )

    assert response_json == expense_db

    photo_filepath_temp = os.path.join(photos_directory, "big_receipt_landscape_from_db.jpg")
    with open(photo_filepath_temp, "wb") as photo_file:
        photo_file.write(expense_db.receiptFile.content)

    from PIL import Image

    photo = Image.open(photo_filepath_temp)
    assert photo.size[0] <= 2048
    assert photo.size[1] <= 2048


def test_post_expense_big_receipt_portrait(expenses, expense_types, expense_receipts, normal_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    photo_filepath = os.path.join(photos_directory, "big_receipt_portrait.jpg")
    with open(photo_filepath, "rb") as photo_file:
        new_expense_details = {
            "expense_type": expense_types[0].id,
            "amount": 40,
            "notes": "Some stuff",
            "expense_date": datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
        }

        response = test_client.post("/expenses",
                               data=new_expense_details,
                               files={"receipt_file": ("big_receipt_portrait.jpg", photo_file, "image/jpeg")},
                               headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    expense_db = db.scalar(
        select(models.Expense)
        .where(models.Expense.expenseDate == datetime.datetime.utcnow().date())
    )

    assert response_json == expense_db

    photo_filepath_temp = os.path.join(photos_directory, "big_receipt_portrait_from_db.jpg")
    with open(photo_filepath_temp, "wb") as photo_file:
        photo_file.write(expense_db.receiptFile.content)

    from PIL import Image

    photo = Image.open(photo_filepath_temp)
    assert photo.size[0] <= 2048
    assert photo.size[1] <= 2048


def test_post_expense_pdf(expenses, expense_types, expense_receipts, normal_user_auth_header):
    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    pdf_filepath = os.path.join(photos_directory, "test_receipt.pdf")
    with open(pdf_filepath, "rb") as pdf_file:
        new_expense_details = {
            "expense_type": expense_types[0].id,
            "amount": 40,
            "notes": "Some stuff",
            "expense_date": datetime.datetime.utcnow().date().strftime("%Y-%m-%d")
        }

        response = test_client.post("/expenses",
                               data=new_expense_details,
                               files={"receipt_file": ("test_receipt.pdf", pdf_file, "application/pdf")},
                               headers=normal_user_auth_header)

        assert response.status_code == 200
        response_json = response.json()

    expense_db = db.scalar(
        select(models.Expense)
        .where(models.Expense.expenseDate == datetime.datetime.utcnow().date())
    )

    assert response_json == expense_db


def test_get_expense_receipt(expenses, expense_receipts, normal_user_auth_header):
    for expense, expense_receipt in zip(expenses, expense_receipts):

        response = test_client.get("/expenses/{expenseId}/receipt".format(expenseId=expense.id), headers=normal_user_auth_header)

        assert response.status_code == 200
        assert response.content == expense_receipt.content


def test_get_expense_types(expense_types, normal_user_auth_header):
    response = test_client.get("/expenses/types", headers=normal_user_auth_header)

    assert response.status_code == 200
    response_json = response.json()

    assert all([et in expense_types for et in response_json])
#

def test_get_expenses(expenses, normal_user_auth_header):
    response = test_client.get("/expenses", headers=normal_user_auth_header)
    assert response.status_code == 200
    response_json = response.json()
    assert all([e in expenses for e in response_json])


def test_patch_expense_transferred(expenses, treasurer_user_auth_header, users):
    for expense in expenses:
        response = test_client.patch("/expenses/{expenseId}/transfer".format(expenseId=expense.id), headers=treasurer_user_auth_header)

        if expense.transferDate is None:
            assert response.status_code == 200
            response_json = response.json()

            assert response_json != expense
            db.refresh(expense)
            assert response_json == expense
            assert expense.transferDate == datetime.datetime.utcnow().date()
            assert expense.treasurerUserId == users[0].id
        else:
            assert response.status_code == 400
            assert response.json().get("detail").get("description") == "This expense does not exist or has already been transferred"
