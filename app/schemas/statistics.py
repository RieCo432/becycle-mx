from uuid import UUID
from pydantic import BaseModel
from app.schemas import Bike


class UserLeaderboard(BaseModel):
    id: UUID
    username: str
    contractsDone: int
    contractsChecked: int
    contractsReturned: int
    depositsCollected: int
    depositAmountCollected: int
    depositsReturned: int
    depositAmountReturned: int


class ClientLeaderboard(BaseModel):
    id: UUID
    fullName: str
    contracts: int
    appointments: int
    appointmentsPending: int
    appointmentsConfirmed: int
    appointmentsDenied: int
    appointmentsCancelled: int


class BikeLeaderboard(Bike):
    contracts: int
