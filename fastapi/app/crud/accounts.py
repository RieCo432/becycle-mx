from datetime import datetime, timezone, date

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, Integer
from starlette import status

from app import schemas, models, crud
from uuid import UUID

from app.services.accounts_helpers import AccountsHelpers
from typing import List

from schemas import DashboardPartQuerySeries
from services import get_interval_timedelta
from services.accounts_helpers import AccountTypes, DashboardDimensions


def get_account(db: Session, account_id: UUID) -> models.Account | None:
    return db.scalar(
        select(models.Account).where(models.Account.id == account_id)
    )


def create_account(new_account_data: schemas.AccountCreate, db: Session) -> models.Account:
    owner_user = None
    if new_account_data.ownerUserId is not None:
        owner_user = crud.users.get_user(db=db, user_id=new_account_data.ownerUserId)
        if owner_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner user not found")
    owner_group = None
    if new_account_data.ownerGroupId is not None:
        owner_group = crud.groups.get_group(db=db, group_id=new_account_data.ownerGroupId)
        if owner_group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner group not found")
        
    if new_account_data.type not in AccountsHelpers.types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account type")
    
    db_account = models.Account(
        name=new_account_data.name.lower(),
        description=new_account_data.description.lower(),
        showInUis=new_account_data.showInUis,
        ownerUserId=owner_user.id if owner_user is not None else None,
        ownerGroupId=owner_group.id if owner_group is not None else None,
        scheduledClosureDate=new_account_data.scheduledClosureDate,
        type=new_account_data.type.lower(),
        isInternal=new_account_data.isInternal,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, ui_filters: List[str] | None = None, types: List[str] | None = None, for_user: models.User | None = None) -> list[models.Account]:
    filter_query = []
    if ui_filters is not None:
        filter_query.append(models.Account.showInUis.op('&&')(ui_filters))
    if types is not None:
        filter_query.append(models.Account.type.in_(types))
    
    accounts = [_ for _ in db.scalars(
        select(models.Account)
        .where(and_(*filter_query))
    )]
    
    final_accounts = []
    
    for account in accounts:
        if not for_user or account.ownerUserId == for_user.id or account.ownerGroupId in [group.id for group in for_user.groups]:
            final_accounts.append(account) 
            
    return final_accounts

def update_account(db: Session, account_id: UUID, updated_account_data: schemas.AccountUpdate) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    if account is None:
        return None
    account.name = updated_account_data.name
    account.description = updated_account_data.description
    account.showInUis = updated_account_data.showInUis
    account.scheduledClosureDate = updated_account_data.scheduledClosureDate
    db.commit()
    db.refresh(account)
    return account

def close_account(account_id: UUID, db: Session, user: models.User) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    account.closedOn = datetime.now(timezone.utc)
    account.closedByUserId = user.id
    db.commit()
    db.refresh(account)
    return account

def reopen_account(account_id: UUID, db: Session) -> models.Account:
    account = get_account(db=db, account_id=account_id)
    account.closedOn = None
    account.closedByUserId = None
    db.commit()
    db.refresh(account)
    return account

def get_all_funds(db: Session) -> list[models.Fund]: # TODO: this should be able to filter by active status
    funds = [_ for _ in db.scalars(
        select(models.Fund)
    )]
    
    return funds


def get_fund(db: Session, fund_id: UUID) -> models.Fund | None:
    fund = db.scalar(
        select(models.Fund).where(models.Fund.id == fund_id)
    )
    return fund


def get_accounts_balance_moment(db: Session, series: schemas.DashboardPartQuerySeries, moment: date, fund_id: UUID | None) -> schemas.DashboardDataSeries:
    account_ids = get_accounts_list_for_series_query(db=db, query=series.query)
    total_balance = get_accounts_balance_moment_raw(db=db, moment=moment, account_ids=account_ids, fund_id=fund_id)

    series_data = schemas.DashboardDataSeries(
        name=series.name,
        data=[schemas.DataPoint(date=moment, value=total_balance)]
    )
    
    return series_data


def get_accounts_balance_moment_raw(db: Session, moment: date, account_ids: list[UUID], fund_id: UUID | None) -> int:
    total_balance = 0
    before_what_day = moment + relativedelta(days=1)

    sum_of_accounts_balances = db.scalar(
        select(func.cast(func.sum(models.TransactionLine.amount), Integer))
        .join(models.TransactionHeader)
        .join(models.Account)
        .where(
            (models.Account.id.in_(account_ids))
            & (models.TransactionHeader.postedOn < before_what_day)
            & ((models.TransactionLine.fundId == fund_id) | (fund_id is None))
        )
    )

    if sum_of_accounts_balances is not None and isinstance(sum_of_accounts_balances, int):
        total_balance = sum_of_accounts_balances
    return total_balance


def get_accounts_accounts_balance_period(db: Session, series: schemas.DashboardPartQuerySeries, start_date: date, end_date: date, interval: str, fund_id: UUID | None) -> schemas.DashboardDataSeries:
    data: list[schemas.DataPoint] = []
    account_ids = get_accounts_list_for_series_query(db=db, query=series.query)
    
    current_period_before: date = end_date
    
    while current_period_before > start_date:
        balance = get_accounts_balance_moment_raw(db=db, moment=current_period_before, account_ids=account_ids, fund_id=fund_id)
        data_point = schemas.DataPoint(
            date=current_period_before,
            value=balance
        )
        data.append(data_point)
        current_period_before -= get_interval_timedelta(interval, current_period_before)
    
    
    series_data = schemas.DashboardDataSeries(
        name=series.name,
        data=data
    )

    return series_data



class CashFlow:
    def __init__(self, credit: int, debit: int):
        self.credit = credit
        self.debit = debit
        self.net = credit + debit


def get_accounts_cashflow_period_raw(db: Session, account_ids: list[UUID], period_start_date: date, period_end_date: date, fund_id: UUID | None) -> CashFlow:
    cashflow_credit: int = 0
    cashflow_debit: int = 0
    
    before: date = period_end_date + relativedelta(days=1)
    after: date = period_start_date + relativedelta(days=1)

    credit = db.scalar(
        select(func.cast(func.sum(models.TransactionLine.amount), Integer))
        .join(models.TransactionHeader)
        .join(models.Account)
        .where(
            (models.Account.id.in_(account_ids))
            & (models.TransactionHeader.postedOn > after)
            & (models.TransactionHeader.postedOn < before)
            & (models.TransactionLine.amount < 0)
            & ((models.TransactionLine.fundId == fund_id) | (fund_id is None))
        )
    )
    if credit is not None and isinstance(credit, int):
        cashflow_credit = credit
    
    debit = db.scalar(
        select(func.cast(func.sum(models.TransactionLine.amount), Integer))
        .join(models.TransactionHeader)
        .join(models.Account)
        .where(
            (models.Account.id.in_(account_ids))
            & (models.TransactionHeader.postedOn > after)
            & (models.TransactionHeader.postedOn < before)
            & (models.TransactionLine.amount > 0)
            & ((models.TransactionLine.fundId == fund_id) | (fund_id is None))
        )
    )
    
    if debit is not None and isinstance(debit, int):
        cashflow_debit = debit

    return CashFlow(credit=cashflow_credit, debit=cashflow_debit)


def get_accounts_cashflow_period(db: Session, series: schemas.DashboardPartQuerySeries, start_date: date, end_date: date, interval: str, fund_id: UUID | None) -> tuple[schemas.DashboardDataSeries, schemas.DashboardDataSeries, schemas.DashboardDataSeries]:
    data_credit: list[schemas.DataPoint] = []
    data_debit: list[schemas.DataPoint] = []
    data_net: list[schemas.DataPoint] = []
    account_ids = get_accounts_list_for_series_query(db=db, query=series.query)
    
    current_period_before: date = end_date
    current_period_since: date = current_period_before - get_interval_timedelta(interval, current_period_before)
    
    while current_period_before > start_date:
        cashflow = get_accounts_cashflow_period_raw(
            db=db,
            account_ids=account_ids,
            period_start_date=current_period_since, 
            period_end_date=current_period_before,
            fund_id=fund_id
        )
        
        data_credit.append(schemas.DataPoint(date=current_period_before, value=cashflow.credit))
        data_debit.append(schemas.DataPoint(date=current_period_before, value=cashflow.debit))
        data_net.append(schemas.DataPoint(date=current_period_before, value=cashflow.net))

        current_period_before = current_period_since
        current_period_since = current_period_before - get_interval_timedelta(interval, current_period_before)
        

    return  (
        schemas.DashboardDataSeries(
            name=series.name,
            data=data_credit,
            meta=schemas.DashboardDataSeriesMeta(flow="credit")
        ), 
        schemas.DashboardDataSeries(
            name=series.name, 
            data=data_debit,
            meta=schemas.DashboardDataSeriesMeta(flow="debit")
        ), 
        schemas.DashboardDataSeries(
            name=series.name, 
            data=data_net,
            meta=schemas.DashboardDataSeriesMeta(flow="net")
        )
    )


def get_accounts_list_for_series_query(db: Session, query: schemas.DashboardSeriesQuery) -> list[UUID]:
    accounts: list[models.Account]
    
    if isinstance(query, list) and all([isinstance(_, UUID) for _ in query]):
        accounts = [_ for _ in db.scalars(select(models.Account).where(models.Account.id.in_(query)))]
    elif isinstance(query, str):
        accounts = [_ for _ in db.scalars(select(models.Account).where(models.Account.type == query))]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Invalid dashboard series"})
    
    return [a.id for a in accounts]


def get_accounts_dashboard_period(db: Session, dashboard_query: schemas.DashboardPartPeriodQuery) -> schemas.DashboardDataPart:
    dashboard_part_series: list[schemas.DashboardDataSeries] = []
    
    for series in dashboard_query.series:
        if dashboard_query.dimension == DashboardDimensions.BALANCE:
            series_data = get_accounts_accounts_balance_period(
                db=db, 
                series=series, 
                start_date=dashboard_query.startDate, 
                end_date=dashboard_query.endDate, 
                interval=dashboard_query.interval,
                fund_id=dashboard_query.fundId
            )
            if series_data is not None:
                dashboard_part_series.append(series_data)
        elif dashboard_query.dimension == DashboardDimensions.CASHFLOW:
            series_data_credit, series_data_debit, series_data_net = get_accounts_cashflow_period(
                db=db, 
                series=series, 
                start_date=dashboard_query.startDate,
                end_date=dashboard_query.endDate, 
                interval=dashboard_query.interval,
                fund_id=dashboard_query.fundId
            )
            if series_data_credit is not None and series.credit:
                dashboard_part_series.append(series_data_credit)
            if series_data_debit is not None and series.debit:
                dashboard_part_series.append(series_data_debit)
            if series_data_net is not None and series.net:
                dashboard_part_series.append(series_data_net)
        

    return schemas.DashboardDataPart(
        name=dashboard_query.name,
        series=dashboard_part_series,
    )


def get_accounts_dashboard_moment(db: Session, dashboard_query: schemas.DashboardPartMomentQuery) -> schemas.DashboardDataPart:
    dashboard_part_series: list[schemas.DashboardDataSeries] = []
    for series in dashboard_query.series:
        if dashboard_query.dimension == DashboardDimensions.BALANCE:
            series_data = get_accounts_balance_moment(db=db, series=series, moment=dashboard_query.moment, fund_id=dashboard_query.fundId)
            dashboard_part_series.append(series_data)
        if dashboard_query.dimension == DashboardDimensions.CASHFLOW:
            raise HTTPException(status_code=400, detail={"description": "Cashflow dimension is not supported for moment dashboard part"})
        
    
    return schemas.DashboardDataPart(
        name=dashboard_query.name, 
        series=dashboard_part_series
    )


def get_accounts_dashboard(db: Session, dashboard_queries: schemas.DashboardQuery) -> schemas.DashboardData:
    dashboard_parts: list[schemas.DashboardDataPart] = []


    last_ditch_start_date: date
    _ = db.scalar(
        select(func.min(models.TransactionHeader.postedOn))
    )
    if _ is not None and isinstance(_, datetime):
        last_ditch_start_date = _.date()
    else:
        raise HTTPException(status_code=400, detail={"description": "No transactions found"})
    
    for dashboard_query in dashboard_queries.queries:
        if dashboard_query.mode == "period" and isinstance(dashboard_query, schemas.DashboardPartPeriodQuery):
            if dashboard_query.startDate is None:
                dashboard_query.startDate = last_ditch_start_date
            if dashboard_query.endDate is None:
                dashboard_query.endDate = datetime.now(timezone.utc).date()
                
            dashboard_parts.append(get_accounts_dashboard_period(db=db, dashboard_query=dashboard_query))
        elif dashboard_query.mode == "moment" and isinstance(dashboard_query, schemas.DashboardPartMomentQuery):
            dashboard_parts.append(get_accounts_dashboard_moment(db=db, dashboard_query=dashboard_query))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": f"Invalid dashboard mode"})
            
    return schemas.DashboardData(name=dashboard_queries.name, parts=dashboard_parts)
        