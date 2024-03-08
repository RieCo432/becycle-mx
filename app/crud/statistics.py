from sqlalchemy import select, func
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from app.crud.users import get_users
from app.crud.clients import get_all_clients
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
