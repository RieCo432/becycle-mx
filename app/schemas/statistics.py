from uuid import UUID
from pydantic import BaseModel


class UserLeaderboard(BaseModel):
    username: str
    contractsDone: int
    contractsChecked: int
    contractsReturned: int
    depositsCollected: int
    depositAmountCollected: int
    depositsReturned: int
    depositAmountReturned: int


class ClientLeaderboard(BaseModel):
    fullName: str
    contracts: int
    appointments: int
    appointmentsPending: int
    appointmentsConfirmed: int
    appointmentsDenied: int
    appointmentsCancelled: int