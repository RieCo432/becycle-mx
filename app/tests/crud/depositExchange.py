import app.crud as crud
from app.tests.pytestFixtures import *


def test_get_deposit_exchange_dates(deposit_exchanges):
    expected_dates = list(set([de.date for de in deposit_exchanges]))
    actual_dates = crud.get_deposit_exchange_dates(db=db)

    assert len(expected_dates) == len(actual_dates)
    assert all([d in expected_dates for d in actual_dates])


def test_get_deposit_exchanges_by_date(deposit_exchanges):
    deposit_exchange_dates = list(set([de.date for de in deposit_exchanges]))

    for d in deposit_exchange_dates:
        expected_deposit_exchanges = [de for de in deposit_exchanges if de.date == d]
        actual_deposit_exchanges = crud.get_deposit_exchanges_by_date(db=db, date_of_exchange=d)

        assert len(expected_deposit_exchanges) == len(actual_deposit_exchanges)
        assert all([de in expected_deposit_exchanges for de in actual_deposit_exchanges])


def test_get_deposit_exchanges_grouped_by_date(deposit_exchanges):
    deposit_exchange_dates = list(set([de.date for de in deposit_exchanges]))
    expected_dict = {d: [de for de in deposit_exchanges if de.date == d] for d in deposit_exchange_dates}
    actual_dict = crud.get_deposit_exchanges_grouped_by_date(db=db)

    assert expected_dict == actual_dict

