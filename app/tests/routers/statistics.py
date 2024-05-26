from fastapi.testclient import TestClient

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
import datetime

test_client = TestClient(app)


def test_get_user_leaderboard(users, contracts, normal_user_auth_header):
    expected_leaderboard = []
    for user in users:
        expected_leaderboard.append({
            "id": str(user.id),
            "username": user.username,
            "contractsDone": len([c for c in contracts if c.workingUserId == user.id]),
            "contractsChecked": len([c for c in contracts if c.checkingUserId == user.id]),
            "contractsReturned": len([c for c in contracts if c.returnAcceptingUserId == user.id]),
            "depositsCollected": len([c for c in contracts if c.depositCollectingUserId == user.id]),
            "depositAmountCollected": sum([c.depositAmountCollected for c in contracts if c.depositCollectingUserId == user.id]),
            "depositsReturned": len([c for c in contracts if c.depositReturningUserId == user.id]),
            "depositAmountReturned": sum([c.depositAmountReturned for c in contracts if c.depositReturningUserId == user.id])
        })

    response = test_client.get("/statistics/users/leaderboard", headers=normal_user_auth_header)

    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json) == len(expected_leaderboard)
    assert all([l_entry in expected_leaderboard for l_entry in response_json])


def test_get_client_leaderboard(contracts, appointments, clients, normal_user_auth_header):
    expected_leaderboard = []
    for client in clients:
        expected_leaderboard.append({
            "id": str(client.id),
        "fullName": f"{client.firstName} {client.lastName}",
        "contracts": len([c for c in contracts if c.clientId == client.id]),
        "appointments": len([a for a in appointments if a.clientId == client.id]),
        "appointmentsConfirmed": len([a for a in appointments if a.clientId == client.id and a.confirmed and not a.cancelled]),
        "appointmentsCancelled": len([a for a in appointments if a.clientId == client.id and a.confirmed and a.cancelled]),
        "appointmentsDenied": len([a for a in appointments if a.clientId == client.id and not a.confirmed and a.cancelled]),
        "appointmentsPending": len([a for a in appointments if a.clientId == client.id and not a.confirmed and not a.cancelled]),
        })

    response = test_client.get("/statistics/clients/leaderboard", headers=normal_user_auth_header)

    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json) == len(expected_leaderboard)
    assert all([l_entry in expected_leaderboard for l_entry in response_json])


def test_get_bike_leaderboard(contracts, bikes, normal_user_auth_header):
    expected_leaderboard = []
    for bike in bikes:
        expected_leaderboard.append({
            "id": str(bike.id),
            "make": bike.make,
            "model": bike.model,
            "colour": bike.colour,
            "decals": bike.decals,
            "serialNumber": bike.serialNumber,
            "contracts": len([c for c in contracts if c.bikeId == bike.id])
        })

    response = test_client.get("/statistics/bikes/leaderboard", headers=normal_user_auth_header)

    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json) == len(expected_leaderboard)
    assert all([l_entry in expected_leaderboard for l_entry in response_json])


def test_get_total_contracts_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 1],
                [today_str, 4]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, 2],
                [today_str, 2]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 1]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/total", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_total_contracts_quarterly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")
    six_quarter_ago_str = (today - relativedelta(months=18)).strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 1],
                [four_quarter_ago_str, 1],
                [three_quarter_ago_str, 2],
                [two_quarter_ago_str, 4],
                [one_quarter_ago_str, 4],
                [today_str, 4]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, 1],
                [five_quarter_ago_str, 2],
                [four_quarter_ago_str, 2],
                [three_quarter_ago_str, 2],
                [two_quarter_ago_str, 2],
                [one_quarter_ago_str, 2],
                [today_str, 2]
            ]
        },
        {
            "name": "kids",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 1],
                [today_str, 1]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/total", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_active_contracts_yearly_two_months_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 1],  # contracts 0
                [today_str, 1]  # contracts 2
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, 1],  # contracts 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 1]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/active", params={"interval": "yearly", "grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_active_contracts_quarterly_two_months_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")
    six_quarter_ago_str = (today - relativedelta(months=18)).strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 1],  # contracts 0
                [four_quarter_ago_str, 1],  # contracts 0
                [three_quarter_ago_str, 1],  # contracts 4
                [two_quarter_ago_str, 3],  # contracts 2, 4, 6
                [one_quarter_ago_str, 3],  # contracts 2, 4, 6
                [today_str, 1]  # contracts 2
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, 1],  # contracts 1
                [five_quarter_ago_str, 1],  # contracts 5
                [four_quarter_ago_str, 1],  # contracts 5
                [three_quarter_ago_str, 1],  # contracts 5
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 1],   # contracts 3
                [today_str, 1]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/active", params={"interval": "quarterly", "grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_active_contracts_yearly_no_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 1],   # contracts 0
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, 1],  # contracts 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 1]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/active", params={"interval": "yearly", "grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_active_contracts_quarterly_no_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")
    six_quarter_ago_str = (today - relativedelta(months=18)).strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 1],  # contracts 0
                [four_quarter_ago_str, 1],  # contracts 0
                [three_quarter_ago_str, 1],  # contracts 4
                [two_quarter_ago_str, 3],  # contracts 2, 4, 6
                [one_quarter_ago_str, 2],  # contracts 2, 6
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, 1],  # contracts 1
                [five_quarter_ago_str, 1],  # contracts 5
                [four_quarter_ago_str, 1],  # contracts 5
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 1],  # contracts 3
                [today_str, 1]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/active", params={"interval": "quarterly", "grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_new_contracts_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 1],   # contracts 0
                [today_str, 3],  # contracts 2, 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, 2],  # contracts 1, 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 1]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/new", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_new_contracts_quarterly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")
    six_quarter_ago_str = (today - relativedelta(months=18)).strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 1],  # contracts 0
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 1],  # contracts 4
                [two_quarter_ago_str, 2],  # contracts 2, 6
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, 1],  # contracts 1
                [five_quarter_ago_str, 1],  # contracts 5
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 1],  # contracts 3
                [today_str, 0]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/new", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_returned_contracts_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 3],  # contracts 0, 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, 1],  # contracts 1
                [today_str, 1]  # contracts 5
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, 0]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/returned", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_returned_contracts_quarterly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")
    six_quarter_ago_str = (today - relativedelta(months=18)).strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 1],  # contracts 0
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, 2]  # contracts 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, 1],  # contracts 1
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 1],  # contracts 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [six_quarter_ago_str, 0],
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/statistics/contracts/returned", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_contracts_percentage_returned_within_grace_period_no_grace_period(contracts, normal_user_auth_header):
    expected_data = {
        "open": 1,
        "in_grace_period": 0,
        "expired": 1,
        "returned": 5,
    }

    response = test_client.get("/statistics/contracts/status", params={"grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_data


def test_get_contracts_percentage_returned_within_grace_period_two_months_grace_period(contracts, normal_user_auth_header):
    expected_data = {
        "open": 1,
        "in_grace_period": 1,
        "expired": 0,
        "returned": 5,
    }

    response = test_client.get("/statistics/contracts/status", params={"grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_data












# VERY EXTENSIVE TEST; BUT RELIES TOO HEAVILY ON ALGORITHM TO GENERATE EXPECTED DATA
# def test_get_active_contracts(contracts, normal_user_auth_header):
#     for grace_period_weeks in range(0, 53):
#         grace_period_days = grace_period_weeks * 7
#         for interval, interval_relativedelta in zip(
#             ["daily", "weekly", "fortnightly", "monthly", "quarterly", "semiyearly", "yearly"],
#             [relativedelta(days=1), relativedelta(weeks=1), relativedelta(weeks=2), relativedelta(months=1), relativedelta(months=3), relativedelta(months=6), relativedelta(years=1)]
#         ):
#             probe_dates = []
#             probe_date = datetime.datetime.utcnow().date()
#             oldest_contract = sorted([c.startDate for c in contracts])[0]
#
#             while probe_date >= oldest_contract:
#                 probe_dates.append(probe_date)
#                 probe_date -= interval_relativedelta
#
#             probe_dates.sort()
#
#             expected_data = sorted([
#                 {
#                     "name": series_name,
#                     "data": [
#                         [probe_date.strftime("%Y-%m-%d"), len([
#                             c for c in contracts
#                             if c.contractType == series_name
#                             and c.startDate <= probe_date
#                             and (c.returnedDate is None or c.returnedDate >= probe_date)
#                             and (c.endDate >= probe_date - relativedelta(days=grace_period_days))
#                         ])] for probe_date in probe_dates
#                     ]
#                 } for series_name in ["standard", "kids", "refugee"]
#
#             ], key=lambda series: series.get("name"))
#
#             response = test_client.get("/statistics/contracts/active", params={"interval": interval, "grace_period": 0}, headers=normal_user_auth_header)
#
#             assert response.status_code == 200
#
#             actual_data = sorted(response.json(), key=lambda series: series.get("name"))
#
#             assert len(actual_data) == len(expected_data)
#             assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
#             assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
#             assert all([all([
#                 series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
#             ]) for series_i in range(len(expected_data))])