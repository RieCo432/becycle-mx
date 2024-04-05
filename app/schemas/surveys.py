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


class PeriBecycleSurvey(BaseModel):
    roadsGreat: bool
    roadsLight: bool
    roadsPotholes: bool
    roadsRubbish: bool
    roadsParking: bool
    roadsDark: bool

    # road users
    usersSafe: bool
    usersBusesUnsafe: bool
    usersCarsUnsafe: bool
    usersTrucksUnsafe: bool
    usersTaxisUnsafe: bool
    usersCyclistsUnsafe: bool
    usersPedestriansUnsafe: bool

    # routes used
    routesRoads: bool
    routesPavements: bool
    routesOffroad: bool

    # accidents
    accidentsNearMisses: int
    accidentsContact: int

    # harassment
    harassmentExperienced: bool
    harassmentSuggestions: str | None = None
