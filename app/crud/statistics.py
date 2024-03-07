from sqlalchemy import select, func
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from app.crud.users import get_users
import bcrypt
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID


def get_leaderboard(db: Session) -> list[schemas.UserLeaderboard]:
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
