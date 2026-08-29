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


def get_accounts_dashboard_series(db: Session, series: schemas.DashboardPartQuerySeries, moment: date) -> schemas.DashboardDataSeries:
    total_balance = 0
    before_what_day = moment + relativedelta(days=1)
    
    account_list = get_accounts_list_for_series_query(db=db, query=series.query)
    
    for account in account_list:
        balance = db.scalar(
            select(func.cast(func.SUM(models.TransactionLine.amount), Integer))
            .join(models.TransactionHeader)
            .join(models.Account)
            .where(
                (models.Account.id == account.id) 
                & (models.TransactionHeader.postedOn < before_what_day)
            )
        )
        if balance is not None and (isinstance(balance, int) or isinstance(balance, float)):
            total_balance += balance
        
    data = schemas.DashboardDataSeries(
        name=series.name,
        data=[schemas.DataPoint(date=moment, value=total_balance)]
    )
    
    return data


def get_accounts_list_for_series_query(db: Session, query: schemas.DashboardSeriesQuery) -> list[models.Account]:
    accounts: list[models.Account]
    
    if isinstance(query, list) and all([isinstance(_, UUID) for _ in query]):
        accounts = [_ for _ in db.scalars(select(models.Account).where(models.Account.id.in_(query)))]
    elif isinstance(query, str):
        accounts = [_ for _ in db.scalars(select(models.Account).where(models.Account.type == query))]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "Invalid dashboard series"})
    
    return accounts


def get_accounts_dashboard_period(db: Session, dashboard_query: schemas.DashboardPartPeriodQuery) -> schemas.DashboardPart:
    dashboard_part_series: list[schemas.DashboardDataSeries] = []
    
    for series in dashboard_query.series:
        if dashboard_query.dimension == DashboardDimensions.BALANCE:
            raise HTTPException(status_code=400, detail={"description": "Balance dimension is not supported for period dashboard part"})
        if dashboard_query.dimension == DashboardDimensions.CASHFLOW:
            raise HTTPException(status_code=400, detail={"description": "Cashflow dimension is not supported for period dashboard part"})

    return schemas.DashboardPart(
        name=dashboard_query.dimension,
        series=dashboard_part_series,
    )


def get_accounts_dashboard_moment(db: Session, dashboard_query: schemas.DashboardPartMomentQuery) -> schemas.DashboardPart:
    dashboard_part_series: list[schemas.DashboardDataSeries] = []
    for series in dashboard_query.series:
        if dashboard_query.dimension == DashboardDimensions.BALANCE:
            series_data = get_accounts_dashboard_series(db=db, series=series, moment=dashboard_query.moment)
            dashboard_part_series.append(series_data)
        if dashboard_query.dimension == DashboardDimensions.CASHFLOW:
            raise HTTPException(status_code=400, detail={"description": "Cashflow dimension is not supported for moment dashboard part"})
        
    
    return schemas.DashboardPart(
        name=dashboard_query.name, 
        series=dashboard_part_series
    )


def get_accounts_dashboard(db: Session, dashboard_queries: schemas.DashboardQuery) -> schemas.Dashboard:
    dashboard_parts: list[schemas.DashboardPart] = []
    
    for dashboard_query in dashboard_queries.queries:
        if dashboard_query.mode == "period" and isinstance(dashboard_query, schemas.DashboardPartPeriodQuery):
            dashboard_parts.append(get_accounts_dashboard_period(db=db, dashboard_query=dashboard_query))
        elif dashboard_query.mode == "moment" and isinstance(dashboard_query, schemas.DashboardPartMomentQuery):
            dashboard_parts.append(get_accounts_dashboard_moment(db=db, dashboard_query=dashboard_query))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": f"Invalid dashboard mode"})
            
    return schemas.Dashboard(name=dashboard_queries.name, parts=dashboard_parts)
        