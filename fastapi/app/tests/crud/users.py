import app.crud as crud
from app.tests.pytestFixtures import *


def test_get_user_by_username_none(users):
    user = crud.get_user_by_username(username=None, db=db)
    assert user is None
