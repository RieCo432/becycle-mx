from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, text, select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.crud.bikes import get_all_bikes
from app.crud.clients import get_all_clients
from app.crud.users import get_users
from app.services import get_interval_timedelta


def get_user_leaderboard(db: Session) -> list[schemas.UserLeaderboard]:
    users = get_users(db=db)

    leaderboard = []

    for user in users:
        contracts_done = len(user.workedContracts)
        contracts_checked = len(user.checkedContracts)
        contracts_returned = len(user.returnedContracts)
        deposits_collected = len(user.depositCollectedContracts)
        deposit_amount_collected = sum([contract.depositAmountCollected for contract in user.depositCollectedContracts])
        deposits_returned = len(user.depositReturnedContracts)
        deposit_amount_returned = sum([contract.depositAmountReturned for contract in user.depositReturnedContracts])

        leaderboard_entry = schemas.UserLeaderboard(
            id=user.id,
            username=user.username,
            contractsDone=contracts_done,
            contractsChecked=contracts_checked,
            contractsReturned=contracts_returned,
            depositsCollected=deposits_collected,
            depositAmountCollected=deposit_amount_collected,
            depositsReturned=deposits_returned,
            depositAmountReturned=deposit_amount_returned
        )

        leaderboard.append(leaderboard_entry)

    return leaderboard


def get_client_leaderboard(db: Session) -> list[schemas.ClientLeaderboard]:
    clients = get_all_clients(db=db)

    leaderboard = []

    for client in clients:
        full_name = "{:s} {:s}".format(client.firstName, client.lastName)
        contracts = len(client.contracts)
        appointments = len(client.appointments)
        appointments_pending = sum(
            [1 if not appointment.confirmed and not appointment.cancelled else 0 for appointment in
             client.appointments])
        appointments_confirmed = sum(
            [1 if appointment.confirmed and not appointment.cancelled else 0 for appointment in client.appointments])
        appointments_cancelled = sum(
            [1 if appointment.confirmed and appointment.cancelled else 0 for appointment in client.appointments])
        appointments_denied = sum(
            [1 if not appointment.confirmed and appointment.cancelled else 0 for appointment in client.appointments])

        leaderboard_entry = schemas.ClientLeaderboard(
            id=client.id,
            fullName=full_name,
            contracts=contracts,
            appointments=appointments,
            appointmentsConfirmed=appointments_confirmed,
            appointmentsCancelled=appointments_cancelled,
            appointmentsDenied=appointments_denied,
            appointmentsPending=appointments_pending,
        )

        leaderboard.append(leaderboard_entry)

    return leaderboard


def get_bike_leaderboard(db: Session) -> list[schemas.BikeLeaderboard]:
    bikes = get_all_bikes(db=db)

    leaderboard = []

    for bike in bikes:
        contracts = len(bike.contracts)

        leaderboard_entry = schemas.BikeLeaderboard(
            id=bike.id,
            make=bike.make,
            model=bike.model,
            colour=bike.colour,
            decals=bike.decals,
            serialNumber=bike.serialNumber,
            contracts=contracts
        )

        leaderboard.append(leaderboard_entry)

    return leaderboard


def get_total_contracts_statistics(db: Session, interval: str, start_date: date | None,
                                   end_date: date | None) -> list[schemas.DataSeries]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()
    interval_timedelta = get_interval_timedelta(interval=interval)

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.count(models.Contract.contractType)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}

    while end_date >= start_date:
        query = db.query(models.Contract.contractType, func.count(models.Contract.contractType))

        counts_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             query.where(models.Contract.startDate <= end_date)
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[end_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([end_date, count])

        end_date -= interval_timedelta

    for breakdown in data_series_by_breakdown:
        data_series_by_breakdown[breakdown].reverse()
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_active_contracts_statistics(db: Session, interval: str, grace_period: int, start_date: date | None,
                                    end_date: date | None) -> list[schemas.DataSeries]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    interval_timedelta = get_interval_timedelta(interval=interval)

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.count(models.Contract.contractType)).group_by(
            models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}

    while end_date >= start_date:

        counts_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType,
                                                                      func.count(models.Contract.contractType))
                                                             .where(
                                                                 (
                                                                         (models.Contract.returnedDate == None)
                                                                         | (models.Contract.returnedDate >= end_date)
                                                                 )
                                                                 & (models.Contract.startDate <= end_date)
                                                                 & (
                                                                             models.Contract.endDate >= end_date - relativedelta(
                                                                         days=grace_period))
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[end_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([end_date, count])

        end_date -= interval_timedelta

    for breakdown in data_series_by_breakdown:
        data_series_by_breakdown[breakdown].reverse()
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_new_contracts_statistics(db: Session, interval: str, start_date: date | None, end_date: date | None) -> list[
    schemas.DataSeries]:
    if start_date is None:
        oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()
        start_date = oldest_contract.startDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    interval_timedelta = get_interval_timedelta(interval=interval)

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.count(models.Contract.contractType)).group_by(
            models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    period_end_date = end_date
    period_start_date = period_end_date - interval_timedelta

    while period_end_date >= start_date:

        counts_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType,
                                                                      func.count(models.Contract.contractType))
                                                             .where(
                                                                 (models.Contract.startDate > period_start_date)
                                                                 & (models.Contract.startDate <= period_end_date)
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[period_end_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([period_end_date, count])

        period_end_date = period_start_date
        period_start_date -= interval_timedelta

    for breakdown in data_series_by_breakdown:
        data_series_by_breakdown[breakdown].reverse()
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_returned_contracts_statistics(db: Session, interval: str, start_date: date | None, end_date: date | None) -> \
list[schemas.DataSeries]:
    if start_date is None:
        oldest_returned_contract = db.query(models.Contract).where(models.Contract.returnedDate != None).order_by(
            models.Contract.returnedDate).first()
        start_date = oldest_returned_contract.returnedDate
    if end_date is None:
        end_date = datetime.utcnow().date()

    interval_timedelta = get_interval_timedelta(interval=interval)

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.count(models.Contract.contractType)).group_by(
            models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    period_end_date = end_date
    period_start_date = period_end_date - interval_timedelta

    while period_end_date >= start_date:

        counts_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType,
                                                                      func.count(models.Contract.contractType))
                                                             .where(
                                                                 (models.Contract.returnedDate != None)
                                                                 & (models.Contract.returnedDate > period_start_date)
                                                                 & (models.Contract.returnedDate <= period_end_date)
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[period_end_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([period_end_date, count])

        period_end_date = period_start_date
        period_start_date -= interval_timedelta

    for breakdown in data_series_by_breakdown:
        data_series_by_breakdown[breakdown].reverse()
        all_series.append(schemas.DataSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_contracts_status(db: Session, grace_period: int, start_date: date | None,
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

    count_open = 0
    count_in_grace_period = 0
    count_expired = 0
    count_returned = 0
    count_unaccounted = 0

    for contract in contracts_in_period:
        if contract.returnedDate is not None:
            count_returned += 1
        elif contract.endDate >= datetime.utcnow().date():
            count_open += 1
        elif contract.endDate + relativedelta(days=grace_period) >= datetime.utcnow().date():
            count_in_grace_period += 1
        elif contract.endDate + relativedelta(days=grace_period) < datetime.utcnow().date():
            count_expired += 1

    contracts_status = {
        "open": count_open,
        "in_grace_period": count_in_grace_period,
        "expired": count_expired,
        "returned": count_returned,
        # **({"???": len(contracts_in_period) - sum([count_open, count_in_grace_period, count_expired, count_returned])} if len(contracts_in_period) - sum([count_open, count_in_grace_period, count_expired, count_returned]) > 0 else {})
    }

    return contracts_status
