from fastapi.testclient import TestClient

from app.tests.pytestFixtures import *
from app.main import app
from dateutil.relativedelta import relativedelta
import datetime

test_client = TestClient(app)


def test_get_deposit_book(contracts, clients, users, deposit_exchanges, normal_user_auth_header):
    expected_data = {
        (datetime.datetime.utcnow() - relativedelta(months=20)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[1].firstName} {clients[1].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[0].username: 40}
                }
            ],
            "diff": {users[0].username: 40},
            "balances": {users[0].username: 40}
        },
        (datetime.datetime.utcnow() - relativedelta(months=18)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[1].firstName} {clients[1].lastName}",
                    "type": "return",
                    "diff_by_username": {users[0].username: -30}
                }
            ],
            "diff": {users[0].username: -30},
            "balances": {users[0].username: 10}
        },
        (datetime.datetime.utcnow() - relativedelta(months=16)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[2].firstName} {clients[2].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[2].username: 40}
                }
            ],
            "diff": {users[2].username: 40},
            "balances": {users[0].username: 10, users[2].username: 40}
        },
        (datetime.datetime.utcnow() - relativedelta(months=15)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[0].firstName} {clients[0].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[0].username: 40}
                }
            ],
            "diff": {users[0].username: 40},
            "balances": {users[0].username: 50, users[2].username: 40}
        },
        (datetime.datetime.utcnow() - relativedelta(months=10)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[0].firstName} {clients[0].lastName}",
                    "type": "return",
                    "diff_by_username": {users[0].username: -30}
                },
                {
                    "title": f"{clients[4].firstName} {clients[4].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[2].username: 40}
                },
                {
                    "title": "Exchange",
                    "type": "exchange",
                    "diff_by_username": {users[0].username: -10, users[2].username: 10}
                }
            ],
            "diff": {users[0].username: -40, users[2].username: 50},
            "balances": {users[0].username: 10, users[2].username: 90}
        },
        (datetime.datetime.utcnow() - relativedelta(months=7)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[2].firstName} {clients[2].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[2].username: 40}
                },
                {
                    "title": f"{clients[4].firstName} {clients[4].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[2].username: 40}
                }
            ],
            "diff": {users[2].username: 80},
            "balances": {users[0].username: 10, users[2].username: 170}
        },
        (datetime.datetime.utcnow() - relativedelta(months=5)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[2].firstName} {clients[2].lastName}",
                    "type": "return",
                    "diff_by_username": {users[2].username: -20}
                }
            ],
            "diff": {users[2].username: -20},
            "balances": {users[0].username: 10, users[2].username: 150}
        },
        (datetime.datetime.utcnow() - relativedelta(months=3)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[3].firstName} {clients[3].lastName}",
                    "type": "deposit",
                    "diff_by_username": {users[2].username: 40}
                },
                {
                    "title": "Exchange",
                    "type": "exchange",
                    "diff_by_username": {users[2].username: -80, users[0].username: 80}
                }
            ],
            "diff": {users[0].username: 80, users[2].username: -40},
            "balances": {users[0].username: 90, users[2].username: 110}
        },
        (datetime.datetime.utcnow() - relativedelta(months=2)).date().strftime("%Y-%m-%d"): {
            "transactions": [
                {
                    "title": f"{clients[4].firstName} {clients[4].lastName}",
                    "type": "return",
                    "diff_by_username": {users[2].username: -30}
                },
                {
                    "title": f"{clients[4].firstName} {clients[4].lastName}",
                    "type": "return",
                    "diff_by_username": {users[2].username: -40}
                }
            ],
            "diff": {users[2].username: -70},
            "balances": {users[0].username: 90, users[2].username: 40}
        },
    }

    response = test_client.get("/finances/deposit-book", headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = response.json().get("dayBalances")

    assert len(actual_data) == len(expected_data)
    assert all([date in actual_data for date in expected_data])
    assert all([expected_data[date].get("diff") == actual_data[date].get("diff") for date in expected_data])
    assert all([expected_data[date].get("balances") == actual_data[date].get("balances") for date in expected_data])
    assert all([len(expected_data[date].get("transactions")) == len(actual_data[date].get("transactions")) for date in expected_data])
    assert all([
        all([
            transaction in expected_data[date].get("transactions")
            for transaction in actual_data[date].get("transactions")
        ]) for date in expected_data])


def test_get_total_deposits_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, sum([
                    contracts[0].depositAmountCollected
                ])],
                [today_str, sum([
                    contracts[0].depositAmountCollected,
                    contracts[2].depositAmountCollected,
                    contracts[4].depositAmountCollected,
                    contracts[6].depositAmountCollected,
                ])]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected
                ])],
                [today_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected
                ])]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, sum([
                    contracts[3].depositAmountCollected
                ])]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/total", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_total_deposits_quarterly(contracts, normal_user_auth_header):
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
                [five_quarter_ago_str, sum([
                    contracts[0].depositAmountCollected
                ])],
                [four_quarter_ago_str, sum([
                    contracts[0].depositAmountCollected
                ])],
                [three_quarter_ago_str, sum([
                    contracts[0].depositAmountCollected,
                    contracts[4].depositAmountCollected
                ])],
                [two_quarter_ago_str, sum([
                    contracts[0].depositAmountCollected,
                    contracts[4].depositAmountCollected,
                    contracts[2].depositAmountCollected,
                    contracts[6].depositAmountCollected,
                ])],
                [one_quarter_ago_str, sum([
                    contracts[0].depositAmountCollected,
                    contracts[4].depositAmountCollected,
                    contracts[2].depositAmountCollected,
                    contracts[6].depositAmountCollected,
                ])],
                [today_str, sum([
                    contracts[0].depositAmountCollected,
                    contracts[4].depositAmountCollected,
                    contracts[2].depositAmountCollected,
                    contracts[6].depositAmountCollected,
                ])]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                ])],
                [five_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])],
                [four_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])],
                [three_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])],
                [two_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])],
                [one_quarter_ago_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])],
                [today_str, sum([
                    contracts[1].depositAmountCollected,
                    contracts[5].depositAmountCollected,
                ])]
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
                [one_quarter_ago_str, sum([
                    contracts[3].depositAmountCollected,
                ])],
                [today_str, sum([
                    contracts[3].depositAmountCollected,
                ])]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/total", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_claimable_deposits_yearly_two_months_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [today_str, sum([contracts[i].depositAmountCollected for i in [2]])]  # contracts 2
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [1]])],  # contracts 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, sum([contracts[i].depositAmountCollected for i in [3]])]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/claimable", params={"interval": "yearly", "grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_claimable_deposits_quarterly_two_months_grace(contracts, normal_user_auth_header):
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
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [four_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [4]])],  # contracts 4
                [two_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 4, 6]])],  # contracts 2, 4, 6
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 4, 6]])],  # contracts 2, 4, 6
                [today_str, sum([contracts[i].depositAmountCollected for i in [2]])]  # contracts 2
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [1]])],  # contracts 1
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
                [four_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
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
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [3]])],   # contracts 3
                [today_str, sum([contracts[i].depositAmountCollected for i in [3]])]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/claimable", params={"interval": "quarterly", "grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_claimable_deposits_yearly_no_grace(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],   # contracts 0
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, sum([contracts[i].depositAmountCollected for i in [3]])]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/claimable", params={"interval": "yearly", "grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_claimable_deposits_quarterly_no_grace(contracts, normal_user_auth_header):
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
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [four_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [4]])],  # contracts 4
                [two_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 4, 6]])],  # contracts 2, 4, 6
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 6]])],  # contracts 2, 6
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [1]])],  # contracts 1
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
                [four_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
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
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [3]])],  # contracts 3
                [today_str, sum([contracts[i].depositAmountCollected for i in [3]])]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/claimable", params={"interval": "quarterly", "grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_collected_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],   # contracts 0
                [today_str, sum([contracts[i].depositAmountCollected for i in [2, 4, 6]])],  # contracts 2, 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [1, 5]])],  # contracts 1, 5
                [today_str, 0]
            ]
        },
        {
            "name": "kids",
            "data": [
                [one_year_ago_str, 0],
                [today_str, sum([contracts[i].depositAmountCollected for i in [3]])]  # contracts 3
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/collected", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_collected_quarterly(contracts, normal_user_auth_header):
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
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0]])],  # contracts 0
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [4]])],  # contracts 4
                [two_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 6]])],  # contracts 2, 6
                [one_quarter_ago_str, 0],
                [today_str, 0]
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [1]])],  # contracts 1
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [5]])],  # contracts 5
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
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [3]])],  # contracts 3
                [today_str, 0]
            ]
        }
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/collected", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_returned_deposits_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "standard",
            "data": [
                [one_year_ago_str, 0],
                [today_str, sum([contracts[i].depositAmountReturned for i in [0, 4, 6]])],  # contracts 0, 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 1
                [today_str, sum([contracts[i].depositAmountReturned for i in [5]])]  # contracts 5
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

    response = test_client.get("/finances/deposits/returned", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_returned_deposits_quarterly(contracts, normal_user_auth_header):
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
                [three_quarter_ago_str, sum([contracts[i].depositAmountReturned for i in [0]])],  # contracts 0
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, 0],
                [today_str, sum([contracts[i].depositAmountReturned for i in [4, 6]])]  # contracts 4, 6
            ]
        },
        {
            "name": "refugee",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 1
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, 0],
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, sum([contracts[i].depositAmountReturned for i in [5]])],  # contracts 5
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

    response = test_client.get("/finances/deposits/returned", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_deposit_flow_yearly(contracts, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_year_ago = today - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    expected_data = sorted([
        {
            "name": "collected",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [0, 1, 5]])],   # contracts 0, 1, 5
                [today_str, sum([contracts[i].depositAmountCollected for i in [2, 3, 4, 6]])],  # contracts 2, 3, 4, 6
            ]
        },
        {
            "name": "returned",
            "data": [
                [one_year_ago_str, -sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 1
                [today_str, -sum([contracts[i].depositAmountReturned for i in [0, 4, 5, 6]])],  # contracts 0, 4, 5, 6
            ]
        },
        {
            "name": "diff",
            "data": [
                [one_year_ago_str, sum([contracts[i].depositAmountCollected for i in [0, 1, 5]]) - sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 0, 1, 5
                [today_str, sum([contracts[i].depositAmountCollected for i in [2, 3, 4, 6]]) - sum([contracts[i].depositAmountReturned for i in [0, 4, 5, 6]])],  # contracts 2, 3, 4, 6
            ]
        },
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/flow", params={"interval": "yearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_collected_quarterly(contracts, normal_user_auth_header):
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
            "name": "collected",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [1]])],
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0, 5]])],  # contracts 0, 5
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [4]])],  # contracts 4
                [two_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 6]])],  # contracts 2, 6
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [3]])],  # contracts 3
                [today_str, 0]
            ]
        },
        {
            "name": "returned",
            "data": [
                [six_quarter_ago_str, -sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 1
                [five_quarter_ago_str, 0],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, -sum([contracts[i].depositAmountReturned for i in [0]])],  # contracts 0
                [two_quarter_ago_str, 0],
                [one_quarter_ago_str, -sum([contracts[i].depositAmountReturned for i in [5]])],  # contracts 5
                [today_str, -sum([contracts[i].depositAmountReturned for i in [4, 6]])]  # contracts 4, 6
            ]
        },
        {
            "name": "diff",
            "data": [
                [six_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [1]]) - sum([contracts[i].depositAmountReturned for i in [1]])],  # contracts 1
                [five_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [0, 5]])],
                [four_quarter_ago_str, 0],
                [three_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [4]]) - sum([contracts[i].depositAmountReturned for i in [0]])],  # contracts 0
                [two_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [2, 6]])],
                [one_quarter_ago_str, sum([contracts[i].depositAmountCollected for i in [3]]) - sum([contracts[i].depositAmountReturned for i in [5]])],  # contracts 5
                [today_str, -sum([contracts[i].depositAmountReturned for i in [4, 6]])]  # contracts 4, 6
            ]
        },
    ], key=lambda series: series.get("name"))

    response = test_client.get("/finances/deposits/flow", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda series: series.get("name"))

    assert len(actual_data) == len(expected_data)
    assert all([len(actual_data[series_i].get("data")) == len(expected_data[series_i].get("data")) for series_i in range(len(expected_data))])
    assert all([actual_series_name in [series.get("name") for series in expected_data] for actual_series_name in [series.get("name") for series in actual_data]])
    assert all([all([
        series_entry in actual_data[series_i].get("data") for series_entry in expected_data[series_i].get("data")
    ]) for series_i in range(len(expected_data))])


def test_get_deposits_status_two_month_grace_period(contracts, normal_user_auth_header):
    expected_data = {
        "open": sum([contracts[i].depositAmountCollected for i in [3]]),
        "in_grace_period": sum([contracts[i].depositAmountCollected for i in [2]]),
        "expired": 0,
        "withheld": sum([contracts[i].depositAmountCollected - contracts[i].depositAmountReturned for i in [0, 1, 4, 5, 6]]),
    }

    response = test_client.get("/finances/deposits/status", params={"grace_period": 62}, headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_data


def test_get_deposits_status_no_grace_period(contracts, normal_user_auth_header):
    expected_data = {
        "open": sum([contracts[i].depositAmountCollected for i in [3]]),
        "in_grace_period": 0,
        "expired": sum([contracts[i].depositAmountCollected for i in [2]]),
        "withheld": sum([contracts[i].depositAmountCollected - contracts[i].depositAmountReturned for i in [0, 1, 4, 5, 6]]),
    }

    response = test_client.get("/finances/deposits/status", params={"grace_period": 0}, headers=normal_user_auth_header)

    assert response.status_code == 200
    assert response.json() == expected_data

def test_get_deposit_return_percentage(contracts, normal_user_auth_header):
    expected_data = [
        {
            "name": "Percentage Returned",
            "type": 'bubble',
            "data": [[-28, 75, 2], [-112, 100, 1], [56, 50, 1], [140, 25, 1]]
        },
        {
            "name": "Trendline",
            "type": 'line',
            "data": [[-120, 100], [-31, 75], [60, 50], [153, 25]]
        }
    ]

    response = test_client.get("/finances/deposits/return-percentage", headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = response.json()

    assert all([bubble in actual_data[0].get("data") for bubble in expected_data[0].get("data")])
    assert all([1.05 * xy[1] >= actual_data[1].get("data")[i][1] >= 0.95 * xy[1] and actual_data[1].get("data")[i][0] == xy[0] for i, xy in enumerate(expected_data[1].get("data"))])

    assert actual_data is not None



#
# @finances.get("/finances/deposits/required-float/worst-case", dependencies=[Depends(dep.get_current_active_user)])
# async def get_worst_case_required_deposit_float(
#         db: Session = Depends(dep.get_db)
# ) -> dict[str, int]:
#     return crud.get_worst_case_required_deposit_float(db=db)
#
#
# @finances.get("/finances/deposits/required-float/realistic", dependencies=[Depends(dep.get_current_active_user)])
# async def get_realistic_case_required_deposit_float(
#         grace_period: int,
#         db: Session = Depends(dep.get_db)
# ) -> dict[str, int]:
#     return crud.get_realistic_required_deposit_float(db=db, grace_period=grace_period)
#
#





def test_get_cashflow_actual_quarterly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [three_quarter_ago_str, -70.0],
                [two_quarter_ago_str, 0.0],
                [one_quarter_ago_str, 0.0],
                [today_str, 0.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [three_quarter_ago_str, 0.0],
                [two_quarter_ago_str, 0.0],
                [one_quarter_ago_str, 100.0],
                [today_str, 0.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [three_quarter_ago_str, -70.0],
                [two_quarter_ago_str, 0.0],
                [one_quarter_ago_str, 100.0],
                [today_str, 0.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/actual", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])


def test_get_cashflow_actual_half_yearly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_half_year_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [one_half_year_ago_str, -70.0],
                [today_str, 0.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [one_half_year_ago_str, 0.0],
                [today_str, 100.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [one_half_year_ago_str, -70.0],
                [today_str, 100.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/actual", params={"interval": "semiyearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])


def test_get_cashflow_provisional_quarterly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")
    four_quarter_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
    five_quarter_ago_str = (today - relativedelta(months=15)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [five_quarter_ago_str, -40.0],
                [four_quarter_ago_str, 0.0],
                [three_quarter_ago_str, -30.0],
                [two_quarter_ago_str, 0.0],
                [one_quarter_ago_str, 0.0],
                [today_str, -120.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [five_quarter_ago_str, 0.0],
                [four_quarter_ago_str, 0.0],
                [three_quarter_ago_str, 0.0],
                [two_quarter_ago_str, 100.0],
                [one_quarter_ago_str, 0.0],
                [today_str, 0.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [five_quarter_ago_str, -40.0],
                [four_quarter_ago_str, 0.0],
                [three_quarter_ago_str, -30.0],
                [two_quarter_ago_str, 100.0],
                [one_quarter_ago_str, 0.0],
                [today_str, -120.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/provisional", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])


def test_get_cashflow_provisional_semi_yearly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_half_year_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    two_half_year_ago_str = (today - relativedelta(months=12)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [two_half_year_ago_str, -40.0],
                [one_half_year_ago_str, -30.0],
                [today_str, -120.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [two_half_year_ago_str, 0.0],
                [one_half_year_ago_str, 100.0],
                [today_str, 0.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [two_half_year_ago_str, -40.0],
                [one_half_year_ago_str, 70.0],
                [today_str, -120.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/provisional", params={"interval": "semiyearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])


def test_get_cashflow_total_quarterly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_quarter_ago_str = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    two_quarter_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    three_quarter_ago_str = (today - relativedelta(months=9)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [three_quarter_ago_str, -70.0],
                [two_quarter_ago_str, -70.0],
                [one_quarter_ago_str, -70.0],
                [today_str, -70.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [three_quarter_ago_str, 0.0],
                [two_quarter_ago_str, 0.0],
                [one_quarter_ago_str, 100.0],
                [today_str, 100.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [three_quarter_ago_str, -70.0],
                [two_quarter_ago_str, -70.0],
                [one_quarter_ago_str, 30.0],
                [today_str, 30.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/total", params={"interval": "quarterly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])


def test_get_cashflow_total_half_yearly(expenses, normal_user_auth_header):
    today = datetime.datetime.utcnow().date()
    today_str = today.strftime("%Y-%m-%d")
    one_half_year_ago_str = (today - relativedelta(months=6)).strftime("%Y-%m-%d")

    expected_data = sorted([
        {
            "name": "Expenses",
            "data": [
                [one_half_year_ago_str, -70.0],
                [today_str, -70.0]
            ]
        },
        {
            "name": "Incomes",
            "data": [
                [one_half_year_ago_str, 0.0],
                [today_str, 100.0]
            ]
        },
        {
            "name": "Differences",
            "data": [
                [one_half_year_ago_str, -70.0],
                [today_str, 30.0]
            ]
        }
    ], key=lambda item: item["name"])

    response = test_client.get("/finances/cashflow/total", params={"interval": "semiyearly"}, headers=normal_user_auth_header)

    assert response.status_code == 200

    actual_data = sorted(response.json(), key=lambda item: item["name"])

    assert len(actual_data) == len(expected_data)
    assert all([series_name in [series.get("name") for series in expected_data] for series_name in [series.get("name") for series in actual_data]])
    for actual_series, expected_series in zip(actual_data, expected_data):
        assert actual_series.get("name") == expected_series.get("name")
        assert all([data_point in actual_series.get("data") for data_point in expected_series.get("data")])