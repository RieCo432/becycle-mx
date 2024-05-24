import app.crud as crud
from app.tests.pytestFixtures import *


def test_get_contract_start_dates(contracts):
    expected_dates = list(set([c.startDate for c in contracts]))
    actual_dates = crud.get_contract_start_dates(db=db)

    assert len(actual_dates) == len(expected_dates)
    assert all([d in actual_dates for d in expected_dates])


def test_get_contract_returned_dates(contracts):
    expected_dates = list(set([c.returnedDate for c in contracts if c.returnedDate is not None]))
    actual_dates = crud.get_contract_returned_dates(db=db)

    assert len(actual_dates) == len(expected_dates)
    assert all([d in actual_dates for d in expected_dates])


def test_get_contracts_by_start_date(contracts):
    dates = [c.startDate for c in contracts]

    for d in dates:
        expected_contracts = [c for c in contracts if c.startDate == d]
        actual_contracts = crud.get_contracts_by_start_date(db=db, start_date=d)

        assert len(expected_contracts) == len(actual_contracts)
        assert all([c in expected_contracts for c in actual_contracts])


def test_get_contracts_by_returned_date(contracts):
    dates = [c.returnedDate for c in contracts if c.returnedDate is not None]

    for d in dates:
        expected_contracts = [c for c in contracts if c.returnedDate == d]
        actual_contracts = crud.get_contracts_by_returned_date(db=db, returned_date=d)

        assert len(expected_contracts) == len(actual_contracts)
        assert all([c in expected_contracts for c in actual_contracts])


def test_get_contracts_grouped_by_start_date(contracts):
    dates = [c.startDate for c in contracts]

    expected_dict = {d: [c for c in contracts if c.startDate == d] for d in dates}
    actual_dict = crud.get_contracts_grouped_by_start_date(db=db)

    assert expected_dict == actual_dict


def test_get_contracts_grouped_by_returned_date(contracts):
    dates = [c.returnedDate for c in contracts if c.returnedDate is not None]

    expected_dict = {d: [c for c in contracts if c.returnedDate == d] for d in dates}
    actual_dict = crud.get_contracts_grouped_by_returned_date(db=db)

    assert expected_dict == actual_dict
