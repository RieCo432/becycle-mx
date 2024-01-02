from sqlalchemy.orm import Session
import app.schemas as schemas
from .contracts import get_contracts_grouped_by_start_date, get_contracts_grouped_by_returned_date
from .depositExchanges import get_deposit_exchanges_grouped_by_date
from fastapi import HTTPException, status


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
                diff_by_username={contract.depositCollectingUser.username: contract.depositAmountCollected}
            ))

        for contract in contracts_grouped_by_returned_date.get(deposit_transaction_date, []):
            deposit_balances_book[deposit_transaction_date].transactions.append(schemas.DepositTransaction(
                title="{} {}".format(contract.client.firstName, contract.client.lastName),
                diff_by_username={contract.depositReturningUser.username: -contract.depositAmountReturned}
            ))

        for deposit_exchange in deposit_exchanges_grouped_by_date.get(deposit_transaction_date, []):
            deposit_balances_book[deposit_transaction_date].transactions.append(schemas.DepositTransaction(
                title="Exchange",
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

    return schemas.DepositBalancesBook(dayBalances=deposit_balances_book)
