from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from app.crud.users import get_users
from app.crud.clients import get_all_clients
from app.crud.bikes import get_all_bikes
import bcrypt
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID


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
        appointments_pending = sum([1 if not appointment.confirmed and not appointment.cancelled else 0 for appointment in client.appointments])
        appointments_confirmed = sum([1 if appointment.confirmed and not appointment.cancelled else 0 for appointment in client.appointments])
        appointments_cancelled = sum([1 if appointment.confirmed and appointment.cancelled else 0 for appointment in client.appointments])
        appointments_denied = sum([1 if not appointment.confirmed and appointment.cancelled else 0 for appointment in client.appointments])

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


def get_total_contracts_statistics(db: Session, interval: int, breakdown: str) -> list[schemas.DateSeries]:
    oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()

    if breakdown == 'contractType':
        col = models.Contract.contractType
        all_categories = [_ for _ in db.scalars(
            db.query(col, func.count(col)).group_by(col)
        )]
    elif breakdown == 'bikeMake':
        col = models.Bike.make
        all_categories = [_ for _ in db.scalars(
            db.query(col, func.count(col)).join(models.Contract).group_by(col)
        )]

    all_series = []
    data_series_by_breakdown = {}
    cutoff_date = oldest_contract.startDate

    while cutoff_date <= datetime.utcnow().date():
        query = db.query(col, func.count(col))
        if breakdown == 'bikeMake':
            query = query.join(models.Contract)

        counts_by_breakdown = {cat: count for cat, count in[_ for _ in
                               query.where(models.Contract.startDate <= cutoff_date)
                               .group_by(col)
                               ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[cutoff_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([cutoff_date, count])

        cutoff_date += relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DateSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series


def get_active_contracts_statistics(db: Session, interval: int, grace_period: int) -> list[schemas.DateSeries]:
    oldest_contract = db.query(models.Contract).order_by(models.Contract.startDate).first()

    all_categories = [_ for _ in db.scalars(
        db.query(models.Contract.contractType, func.count(models.Contract.contractType)).group_by(models.Contract.contractType)
    )]

    all_series = []
    data_series_by_breakdown = {}
    probe_date = oldest_contract.startDate

    while probe_date <= datetime.utcnow().date():

        counts_by_breakdown = {cat: count for cat, count in [_ for _ in
                                                             db.query(models.Contract.contractType, func.count(models.Contract.contractType))
                                                             .where(
                                                                 (models.Contract.startDate <= probe_date)
                                                                 & (models.Contract.endDate >= probe_date - relativedelta(days=grace_period))
                                                             )
                                                             .group_by(models.Contract.contractType)
                                                             ]}
        for breakdown in all_categories:
            count = counts_by_breakdown.get(breakdown, 0)
            if breakdown not in data_series_by_breakdown:
                data_series_by_breakdown[breakdown] = [[probe_date, count]]
            else:
                data_series_by_breakdown[breakdown].append([probe_date, count])

        probe_date += relativedelta(days=interval)

    for breakdown in data_series_by_breakdown:
        all_series.append(schemas.DateSeries(
            name=breakdown,
            data=data_series_by_breakdown[breakdown]
        ))

    return all_series
