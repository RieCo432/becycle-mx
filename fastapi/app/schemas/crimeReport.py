from .contract import CrimeReport, Contract
from .bike import Bike
from .client import Client


class ContractWithBikeAndClient(Contract):
    bike: Bike
    client: Client


class CrimeReportFull(CrimeReport):
    contract: ContractWithBikeAndClient