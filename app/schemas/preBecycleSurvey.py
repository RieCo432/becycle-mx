from pydantic import BaseModel


class PreBecycleSurvey(BaseModel):
    hurdleSafety: bool
    hurdleMoney: bool
    hurdleTime: bool
    hurdleSweating: bool
    hurdleComfort: bool
    hurdleDistance: bool
    hurdleOther: str | None = None

    # motivation
    motivationMoney: bool
    motivationHealth: bool
    motivationEnvironmental: bool
    motivationOther: str | None = None

    # options considered
    consideredNewOnline: bool
    consideredNewShop: bool
    consideredUsed: bool
    consideredLendingPrivate: bool
    consideredLendingBecycle: bool
    consideredOther: str | None = None

    # training
    trainingExperienceMonths: int
    trainingFormal: bool
    trainingConfidence: int
    trainingRules: bool
    trainingDriver: bool

    # interest
    interestMaintenanceDesired: int
    interestMaintenanceCurrent: int
