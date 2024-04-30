from math import ceil

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sklearn import linear_model

import app.models as models
import app.schemas as schemas
from .contracts import get_contracts_grouped_by_start_date, get_contracts_grouped_by_returned_date
from .depositExchanges import get_deposit_exchanges_grouped_by_date
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def get_deposit_balances_book(db: Session) -> schemas.DepositBalancesBook:
    contracts_grouped_by_start_date = get_contracts_grouped_by_start_date(db=db)
    contracts_grouped_by_returned_date = get_contracts_grouped_by_returned_date(db=db)

    deposit_exchanges_grouped_by_date = get_deposit_exchanges_grouped_by_date(db=db)

    deposit_transaction_dates = sorted(list(
        contracts_grouped_by_start_date.keys()
        | contracts_grouped_by_returned_date.keys()
        | deposit_exchanges_grouped_by_date.keys()))

    deposit_balances_book = {}
    previous_balances = {}

    for deposit_transaction_date in deposit_transaction_dates:

        deposit_balances_book[deposit_transaction_date] = schemas.DepositDayBalances()

        for contract in contracts_grouped_by_start_date.get(deposit_transaction_date, []):
            deposit_balances_book[deposit_transaction_date].transactions.append(schemas.DepositTransaction(
                title="{} {}".format(contract.client.firstName, contract.client.lastName),
                type="deposit",
                diff_by_username={contract.depositCollectingUser.username: contract.depositAmountCollected}
            ))

        for contract in contracts_grouped_by_returned_date.get(deposit_transaction_date, []):
            deposit_balances_book[deposit_transaction_date].transactions.append(schemas.DepositTransaction(
                title="{} {}".format(contract.client.firstName, contract.client.lastName),
                type="return",
                diff_by_username={contract.depositReturningUser.username: -contract.depositAmountReturned}
            ))

        for deposit_exchange in deposit_exchanges_grouped_by_date.get(deposit_transaction_date, []):
            deposit_balances_book[deposit_transaction_date].transactions.append(schemas.DepositTransaction(
                title="Exchange",
                type="exchange",
                diff_by_username={
                    deposit_exchange.fromUser.username: -deposit_exchange.amount,
                    deposit_exchange.toUser.username: deposit_exchange.amount
                }
            ))

        for deposit_transaction in deposit_balances_book[deposit_transaction_date].transactions:
            for username, diff in deposit_transaction.diff_by_username.items():
                if username not in deposit_balances_book[deposit_transaction_date].diff:
                    deposit_balances_book[deposit_transaction_date].diff[username] = diff
                else:
                    deposit_balances_book[deposit_transaction_date].diff[username] += diff

        deposit_balances_book[deposit_transaction_date].balances = {username: balance for username, balance in previous_balances.items() if balance != 0}

        for username, diff in deposit_balances_book[deposit_transaction_date].diff.items():
            if diff == 0:
                continue
            deposit_balances_book[deposit_transaction_date].balances[username] = deposit_balances_book[deposit_transaction_date].balances.get(username, 0) + diff
            if deposit_balances_book[deposit_transaction_date].balances[username] < 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"description": "One of the deposit bearers has a negative balance!"},
                    headers={"WWW-Authenticate": "Bearer"}
                )

        previous_balances = deposit_balances_book[deposit_transaction_date].balances

    for date in deposit_balances_book.keys():
        if "BANK" not in deposit_balances_book[date].diff and "BANK" in deposit_balances_book[date].balances:
            deposit_balances_book[date].balances.pop("BANK")

    return schemas.DepositBalancesBook(dayBalances=deposit_balances_book)


def get_total_deposits(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        interval: int | None = None) -> list[schemas.DataSeries]:
    if interval == 0:
        interval = 1
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    period_start_date = start_date
    period_end_date = start_date + relativedelta(days=interval)

    while period_start_date <= end_date:

        deposit_sum_by_breakdown = {cat: deposit_sum for cat, deposit_sum in [_ for _ in
                                                             db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected))
                                                             .where(
                                                                 (models.Contract.startDate <= period_start_date)
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            deposit_sum = deposit_sum_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[period_start_date, deposit_sum]]
            else:
                data_series_by_breakdown[breakdown].append([period_start_date, deposit_sum])

        period_start_date = period_end_date
        period_end_date = period_start_date + relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_claimable_deposits(db: Session, interval: int, grace_period: int, start_date: date | None, end_date: date | None) -> list[schemas.DataSeries]:
    if interval == 0:
        interval = 1
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}

    while start_date <= end_date:

        claimable_deposits_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected))
                                                             .where(
                                                                 (
                                                                     (models.Contract.returnedDate == None)
                                                                     | (models.Contract.returnedDate >= start_date)
                                                                 )
                                                                 & (models.Contract.startDate <= start_date)
                                                                 & (models.Contract.endDate >= start_date - relativedelta(days=grace_period))
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = claimable_deposits_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[start_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([start_date, count])

        start_date += relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_collected_deposits(db: Session, interval: int, start_date: date | None, end_date: date | None) -> list[schemas.DataSeries]:
    if interval == 0:
        interval = 1

    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    period_start_date = start_date
    period_end_date = period_start_date + relativedelta(days=interval)

    while period_start_date <= end_date:

        deposits_collected_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountCollected))
                                                             .where(
                                                                 (models.Contract.startDate >= period_start_date)
                                                                 & (models.Contract.startDate < period_end_date)
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = deposits_collected_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[period_start_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([period_start_date, count])

        period_start_date = period_end_date
        period_end_date = period_start_date + relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_returned_deposits(db: Session, interval: int, start_date: date | None, end_date: date | None) -> list[schemas.DataSeries]:
    if interval == 0:
        interval = 1
    if start_date is None:
        oldest_returned_contract = db.query(models.Contract).where(models.Contract.returnedDate != None).order_by(models.Contract.returnedDate).first()
        start_date = oldest_returned_contract.returnedDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountReturned)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    period_start_date = start_date
    period_end_date = start_date + relativedelta(days=interval)

    while period_start_date <= end_date:

        deposits_returned_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType, func.sum(models.Contract.depositAmountReturned))
                                                             .where(
                                                                 (models.Contract.returnedDate != None)
                                                                 & (models.Contract.returnedDate >= period_start_date)
                                                                 & (models.Contract.returnedDate < period_end_date)
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = deposits_returned_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[period_start_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([period_start_date, count])

        period_start_date = period_end_date
        period_end_date = period_start_date + relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_deposit_flow(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[schemas.DataSeries]:
    if interval == 0:
        interval = 1

    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    categories = ["collected", "returned", "diff"]
    data_series_by_breakdown = {cat: [] for cat in categories}

    all_series = []
    period_start_date = start_date
    period_end_date = start_date + relativedelta(days=interval)

    while period_start_date <= end_date:

        deposit_flow_collected = db.scalar(
            select(func.coalesce(func.sum(models.Contract.depositAmountCollected), 0))
            .where(
                (models.Contract.startDate >= period_start_date)
                & (models.Contract.startDate < period_end_date)
            )
        )
        data_series_by_breakdown["collected"].append([period_start_date, deposit_flow_collected])

        deposit_flow_returned = db.scalar(
            select(func.coalesce(func.sum(models.Contract.depositAmountReturned), 0))
            .where(
                (models.Contract.returnedDate != None)
                & (models.Contract.returnedDate >= period_start_date)
                & (models.Contract.returnedDate < period_end_date)
            )
        )
        data_series_by_breakdown["returned"].append([period_start_date, -deposit_flow_returned])

        deposit_flow_diff = deposit_flow_collected - deposit_flow_returned

        data_series_by_breakdown["diff"].append([period_start_date, deposit_flow_diff])

        period_start_date = period_end_date
        period_end_date = period_start_date + relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_deposits_status(db: Session, grace_period: int, start_date: date | None,
                                                          end_date: date | None) -> dict[str, int]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    contracts_in_period = [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(
                (models.Contract.endDate >= start_date)
                & (models.Contract.startDate < end_date)
            )
        )
    ]

    deposits_open = 0
    deposits_in_grace_period = 0
    deposits_expired = 0
    deposits_withheld = 0
    deposits_unaccounted = 0

    for contract in contracts_in_period:
        if contract.returnedDate is not None:
            deposits_withheld += contract.depositAmountCollected - contract.depositAmountReturned
        elif contract.endDate >= datetime.utcnow().date():
            deposits_open += contract.depositAmountCollected
        elif contract.endDate + relativedelta(days=grace_period) >= datetime.utcnow().date():
            deposits_in_grace_period += contract.depositAmountCollected
        elif contract.endDate + relativedelta(days=grace_period) < datetime.utcnow().date():
            deposits_expired += contract.depositAmountCollected
        else:
            deposits_unaccounted += contract.depositAmountCollected

    deposits_status = {
        "open": deposits_open,
        "in_grace_period": deposits_in_grace_period,
        "expired": deposits_expired,
        "withheld": deposits_withheld,
    }

    if deposits_unaccounted > 0:
        deposits_status["???"] = deposits_unaccounted

    return deposits_status


def get_percentages_of_deposit_returned_by_contract_age(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[list[int]]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()
    if interval == 0:
        interval = 1

    all_returned_contracts_in_period = [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(
                (models.Contract.returnedDate != None)
                & (models.Contract.returnedDate >= start_date)
                & (models.Contract.returnedDate <= end_date)
            )
        )
    ]

    percentages_of_deposit_returned_by_contract_age = []

    for contract in all_returned_contracts_in_period:
        days_after_contract_end = (contract.returnedDate - contract.endDate).days
        number_of_intervals_after_contract_end = days_after_contract_end // interval

        percentages_of_deposit_returned_by_contract_age.append([int(number_of_intervals_after_contract_end * interval),
                                                                int(100 * contract.depositAmountReturned / contract.depositAmountCollected)])

    return percentages_of_deposit_returned_by_contract_age


def get_deposit_return_percentage_trendline(percentages_of_deposit_returned_by_contract_age: list[list[int]]) -> dict[str, float]:
    x_raw = np.array([xy[0] for xy in percentages_of_deposit_returned_by_contract_age])
    y_raw = np.array([xy[1] for xy in percentages_of_deposit_returned_by_contract_age])

    X = x_raw[:, np.newaxis]
    y = y_raw[:, np.newaxis]

    reg = linear_model.LinearRegression()

    reg.fit(X, y)
    a = reg.coef_[0, 0]
    c = reg.intercept_[0]

    return {"a": a, "c": c}


def get_deposit_return_percentage(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[schemas.DataSeriesWithType]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()
    if interval == 0:
        interval = 1

    percentages_of_deposit_returned_by_contract_age = get_percentages_of_deposit_returned_by_contract_age(db=db, interval=interval, start_date=start_date, end_date=end_date)

    trendline = get_deposit_return_percentage_trendline(percentages_of_deposit_returned_by_contract_age)

    trendline_samples = [[int(x), min([int(trendline["a"]*x+trendline["c"]), 100])] for x in sorted(list(set([xy[0] for xy in percentages_of_deposit_returned_by_contract_age])))]

    return [
        schemas.DataSeriesWithType(
            name="Percentage of Deposit Returned by Age of Contract",
            type='scatter',
            data=percentages_of_deposit_returned_by_contract_age
        ),
        schemas.DataSeriesWithType(
            name="Trendline",
            type='line',
            data=trendline_samples
        )
    ]


def get_worst_case_required_deposit_float(db: Session, interval: int) -> dict[str: int]:
    if interval == 0:
        interval = 1
    trendline = get_deposit_return_percentage_trendline(get_percentages_of_deposit_returned_by_contract_age(db=db, interval=interval))

    all_unreturned_contracts = [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(models.Contract.returnedDate == None)
        )
    ]

    total_returnable_deposit_amount = 0
    estimated_return_deposits_amount = 0

    for contract in all_unreturned_contracts:
        total_returnable_deposit_amount += contract.depositAmountCollected
        days_after_end_date = (datetime.utcnow().date() - contract.endDate).days
        percentage = (trendline["a"] * days_after_end_date + trendline["c"]) / 100.0
        estimated_return_deposits_amount += int(ceil(contract.depositAmountCollected * percentage))

    return {
        "required": estimated_return_deposits_amount,
        "excess": total_returnable_deposit_amount - estimated_return_deposits_amount
    }


def get_realistic_required_deposit_float(db: Session, interval: int, grace_period: int) -> dict[str: int]:
    if interval == 0:
        interval = 1
    all_returned_contracts = [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(models.Contract.returnedDate != None)
        )
    ]

    days_returned_after_contract_end = [(contract.returnedDate - contract.endDate).days for contract in
                                        all_returned_contracts]
    mean_days_returned_after_contract_end = np.mean(days_returned_after_contract_end)

    trendline = get_deposit_return_percentage_trendline(get_percentages_of_deposit_returned_by_contract_age(db=db, interval=interval))

    all_unreturned_contracts = [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(models.Contract.returnedDate == None)
        )
    ]

    total_returnable_deposit_amount = 0
    estimated_return_deposits_amount = 0

    for contract in all_unreturned_contracts:
        days_after_contract_end = (datetime.utcnow().date() - contract.endDate).days
        if days_after_contract_end > grace_period:
            continue
        total_returnable_deposit_amount += contract.depositAmountCollected
        returned_days_after_end = max([
            mean_days_returned_after_contract_end,
            days_after_contract_end
        ])
        percentage = (trendline["a"] * returned_days_after_end + trendline["c"]) / 100.0
        estimated_return_deposits_amount += int(ceil(contract.depositAmountCollected * percentage))

    return {
        "required": estimated_return_deposits_amount,
        "excess": total_returnable_deposit_amount - estimated_return_deposits_amount
    }


def get_actual_cashflow(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[schemas.DataSeries]:
    if start_date is None:
        oldest_expense = db.query(models.Expense).where(models.Expense.transferDate != None).order_by(models.Expense.transferDate).first()
        start_date = oldest_expense.transferDate
    if end_date is None:
        newest_expense = db.query(models.Expense).where(models.Expense.transferDate != None).order_by(models.Expense.transferDate.desc()).first()
        end_date = newest_expense.transferDate
    if interval == 0:
        interval = 1

    interval_start_date = start_date
    interval_end_date = start_date + relativedelta(days=interval)

    expense_series = []
    income_series = []
    diff_series = []

    while interval_start_date <= end_date:
        expenses_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.transferDate >= interval_start_date)
                & (models.Expense.transferDate < interval_end_date)
                & (models.Expense.amount < 0)
            )
        )

        income_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.transferDate >= interval_start_date)
                & (models.Expense.transferDate < interval_end_date)
                & (models.Expense.amount > 0)
            )
        )

        expense_series.append([interval_start_date, expenses_in_interval])
        income_series.append([interval_start_date, income_in_interval])
        diff_series.append([interval_start_date, income_in_interval + expenses_in_interval])

        interval_start_date = interval_end_date
        interval_end_date += relativedelta(days=interval)

    return [
        schemas.DataSeries(
            name="Expenses",
            data=expense_series
        ),
        schemas.DataSeries(
            name="Incomes",
            data=income_series
        ),
        schemas.DataSeries(
            name="Differences",
            data=diff_series
        )
    ]


def get_provisional_cashflow(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[schemas.DataSeries]:
    if start_date is None:
        oldest_expense = db.query(models.Expense).order_by(models.Expense.expenseDate).first()
        start_date = oldest_expense.expenseDate
    if end_date is None:
        newest_expense = db.query(models.Expense).order_by(models.Expense.expenseDate.desc()).first()
        end_date = newest_expense.expenseDate
    if interval == 0:
        interval = 1

    interval_start_date = start_date
    interval_end_date = start_date + relativedelta(days=interval)

    expense_series = []
    income_series = []
    diff_series = []

    while interval_start_date <= end_date:
        expenses_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.expenseDate >= interval_start_date)
                & (models.Expense.expenseDate < interval_end_date)
                & (models.Expense.amount < 0)
            )
        )

        income_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.expenseDate >= interval_start_date)
                & (models.Expense.expenseDate < interval_end_date)
                & (models.Expense.amount > 0)
            )
        )

        expense_series.append([interval_start_date, expenses_in_interval])
        income_series.append([interval_start_date, income_in_interval])
        diff_series.append([interval_start_date, income_in_interval + expenses_in_interval])

        interval_start_date = interval_end_date
        interval_end_date += relativedelta(days=interval)

    return [
        schemas.DataSeries(
            name="Expenses",
            data=expense_series
        ),
        schemas.DataSeries(
            name="Incomes",
            data=income_series
        ),
        schemas.DataSeries(
            name="Differences",
            data=diff_series
        )
    ]


def get_total_cashflow(db: Session, interval: int, start_date: date | None = None, end_date: date | None = None) -> list[schemas.DataSeries]:
    if start_date is None:
        oldest_expense = db.query(models.Expense).where(models.Expense.transferDate != None).order_by(models.Expense.transferDate).first()
        start_date = oldest_expense.transferDate
    if end_date is None:
        newest_expense = db.query(models.Expense).where(models.Expense.transferDate != None).order_by(models.Expense.transferDate.desc()).first()
        end_date = newest_expense.transferDate
    if interval == 0:
        interval = 1

    period_start_date = start_date

    expense_series = []
    income_series = []
    diff_series = []

    while period_start_date <= end_date:
        expenses_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.transferDate <= period_start_date)
                & (models.Expense.amount < 0)
            )
        )

        income_in_interval = db.scalar(
            select(func.coalesce(func.sum(models.Expense.amount), 0))
            .where(
                (models.Expense.transferDate <= period_start_date)
                & (models.Expense.amount > 0)
            )
        )

        expense_series.append([period_start_date, expenses_in_interval])
        income_series.append([period_start_date, income_in_interval])
        diff_series.append([period_start_date, income_in_interval + expenses_in_interval])

        period_start_date += relativedelta(days=interval)

    return [
        schemas.DataSeries(
            name="Expenses",
            data=expense_series
        ),
        schemas.DataSeries(
            name="Incomes",
            data=income_series
        ),
        schemas.DataSeries(
            name="Differences",
            data=diff_series
        )
    ]



