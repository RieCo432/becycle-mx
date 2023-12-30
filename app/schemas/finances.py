from pydantic import BaseModel
from datetime import date
from uuid import UUID


class DepositTransaction(BaseModel):
    title: str
    diff_by_username: dict[str, int]


class DepositDayBalances(BaseModel):
    transactions: list[DepositTransaction] = []
    diff: dict[str, int] = {}
    balances: dict[str, int] = {}


class DepositBalancesBook(BaseModel):
    dayBalances: dict[date, DepositDayBalances] = {}

