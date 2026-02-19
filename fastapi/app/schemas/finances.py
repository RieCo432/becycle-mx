from datetime import date

from pydantic import BaseModel


class DepositTransaction(BaseModel):
    title: str
    type: str
    diff_by_username: dict[str, int]


class DepositDayBalances(BaseModel):
    transactions: list[DepositTransaction] = []
    diff: dict[str, int] = {}
    balances: dict[str, int] = {}


class DepositBalancesBook(BaseModel):
    dayBalances: dict[date, DepositDayBalances] = {}
    
    
    
class DepositAccountTransaction(BaseModel):
    title: str
    event: str
    diff_by_account: dict[str, int] = {}
    
    
class DepositAccountsDayBalances(BaseModel):
    transactions: list[DepositAccountTransaction] = []
    diff: dict[str, int] = {}
    balances: dict[str, int] = {}
    
    
class DepositAccountBalances(BaseModel):
    dayBalances: dict[date, DepositAccountsDayBalances] = {}

