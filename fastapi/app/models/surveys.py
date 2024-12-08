from datetime import datetime
from uuid import uuid4

from sqlalchemy import text, Boolean, Text, Integer, UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class PreBecycleSurvey(Base):
    __tablename__ = "prebecyclesurvey"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    datetime: Mapped[datetime] = mapped_column("datetime", DateTime, nullable=False, quote=False, default=datetime.utcnow(), server_default=text("current_timestamp"))
    # hurdles
    hurdleSafety: Mapped[bool] = mapped_column("hurdlesafety", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleMoney: Mapped[bool] = mapped_column("hurdlemoney", Boolean, default=False, server_default=text("FALSE"),
                                             nullable=False, quote=False)
    hurdleTime: Mapped[bool] = mapped_column("hurdletime", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleSweating: Mapped[bool] = mapped_column("hurdlesweating", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleComfort: Mapped[bool] = mapped_column("hurdlecomfort", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleDistance: Mapped[bool] = mapped_column("hurdledistance", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleOther: Mapped[str] = mapped_column("hurdleother", Text, default=None, server_default=text("NULL"), nullable=True, quote=False)

    # motivation
    motivationMoney: Mapped[bool] = mapped_column("motivationmoney", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    motivationHealth: Mapped[bool] = mapped_column("motivationhealth", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    motivationEnvironmental: Mapped[bool] = mapped_column("motivationenvironmental", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                             quote=False)
    motivationOther: Mapped[str] = mapped_column("motivationother", Text, default=None, server_default=text("NULL"), nullable=True,
                                             quote=False)

    # options considered
    consideredNewOnline: Mapped[bool] = mapped_column("considerednewonline", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    consideredNewShop: Mapped[bool] = mapped_column("considerednewshop", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredUsed: Mapped[bool] = mapped_column("consideredused", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredLendingPrivate: Mapped[bool] = mapped_column("consideredlendingprivate", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredLendingBecycle: Mapped[bool] = mapped_column("consideredlendingbecycle", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredOther: Mapped[str] = mapped_column("consideredother", Text, default=None,
                                                      server_default=text("NULL"), nullable=True,
                                                      quote=False)

    # training
    trainingExperienceMonths: Mapped[int] = mapped_column("trainingexperience", Integer, nullable=False, quote=False)
    trainingFormal: Mapped[bool] = mapped_column("trainingformal", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    trainingConfidence: Mapped[int] = mapped_column("trainingconfidence", Integer, nullable=False, quote=False)
    trainingRules: Mapped[bool] = mapped_column("trainingrules", Boolean, default=False, server_default=text("FALSE"),
                                                 nullable=False,
                                                 quote=False)
    trainingDriver: Mapped[bool] = mapped_column("trainingdriver", Boolean, default=False, server_default=text("FALSE"),
                                                nullable=False,
                                                quote=False)

    # interest
    interestMaintenanceDesired: Mapped[int] = mapped_column("interestmaintenancedesired", Integer, nullable=False, quote=False)
    interestMaintenanceCurrent: Mapped[int] = mapped_column("interestmaintenancecurrent", Integer, nullable=False, quote=False)


class PeriBecycleSurvey(Base):
    __tablename__ = "peribecyclesurvey"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    datetime: Mapped[datetime] = mapped_column("datetime", DateTime, nullable=False, quote=False, default=datetime.utcnow(), server_default=text("current_timestamp"))

    # service satisfaction
    serviceSatisfactionGetBike: Mapped[int] = mapped_column("servicesatisfactiongetbike", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))
    serviceSatisfactionFixBike: Mapped[int] = mapped_column("servicesatisfactionfixbike", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))
    serviceSatisfactionLearn: Mapped[int] = mapped_column("servicesatisfactionlearn", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))

    # roads opinion
    roadsGreat: Mapped[bool] = mapped_column("roadsgreat", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    roadsLight: Mapped[bool] = mapped_column("roadslight", Boolean, default=False, server_default=text("FALSE"),
                                             nullable=False, quote=False)
    roadsPotholes: Mapped[bool] = mapped_column("roadspotholes", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    roadsRubbish: Mapped[bool] = mapped_column("roadsrubbish", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    roadsParking: Mapped[bool] = mapped_column("roadsparking", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    roadsDark: Mapped[bool] = mapped_column("roadsdark", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)

    # road users
    usersSafe: Mapped[bool] = mapped_column("userssafe", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    usersBusesUnsafe: Mapped[bool] = mapped_column("usersbusesunsafe", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    usersCarsUnsafe: Mapped[bool] = mapped_column("userscarsunsafe", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                             quote=False)
    usersTrucksUnsafe: Mapped[bool] = mapped_column("userstrucksunsafe", Boolean, default=None, server_default=text("FALSE"),
                                            nullable=True,
                                            quote=False)
    usersTaxisUnsafe: Mapped[bool] = mapped_column("userstaxisunsafe", Boolean, default=None, server_default=text("FALSE"), nullable=True,
                                             quote=False)
    usersCyclistsUnsafe: Mapped[bool] = mapped_column("userscyclistsunsafe", Boolean, default=None, server_default=text("FALSE"),
                                                  nullable=True, quote=False)
    usersPedestriansUnsafe: Mapped[bool] = mapped_column("userspedestriansunsafe", Boolean, default=None,
                                                     server_default=text("FALSE"), nullable=True, quote=False)

    # routes used
    routesRoads: Mapped[bool] = mapped_column("routesroads", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    routesPavements: Mapped[bool] = mapped_column("routespavements", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    routesOffroad: Mapped[bool] = mapped_column("routesoffroad", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)

    # accidents
    accidentsNearMisses: Mapped[int] = mapped_column("accidentsnearmisses", Integer, nullable=False, quote=False, default=0, server_default=text('0'))
    accidentsContact: Mapped[int] = mapped_column("accidentscontact", Integer, nullable=False, quote=False, default=0, server_default=text('0'))

    # harassment
    harassmentExperienced: Mapped[bool] = mapped_column("harassmentexperienced", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    harassmentSuggestions: Mapped[str] = mapped_column("harassmentsuggestions", Text, nullable=True, quote=False)


class PostBecycleSurvey(Base):
    __tablename__ = "postbecyclesurvey"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)
    datetime: Mapped[datetime] = mapped_column("datetime", DateTime, nullable=False, quote=False, default=datetime.utcnow(), server_default=text("current_timestamp"))

    # service satisfaction
    serviceSatisfactionGetBike: Mapped[int] = mapped_column("servicesatisfactiongetbike", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))
    serviceSatisfactionFixBike: Mapped[int] = mapped_column("servicesatisfactionfixbike", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))
    serviceSatisfactionLearn: Mapped[int] = mapped_column("servicesatisfactionlearn", Integer, nullable=False, quote=False,
                                                     default=0, server_default=text('0'))

    # stopped cycling
    reasonStoppedCycling: Mapped[bool] = mapped_column("reasonstoppedcycling", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    reasonLeavingAberdeen: Mapped[bool] = mapped_column("reasonleavingaberdeen", Boolean, default=False,
                                                       server_default=text("FALSE"),
                                                       nullable=False, quote=False)

    # if stopped, why

    issueSafety: Mapped[bool] = mapped_column("issuesafety", Boolean, default=False, server_default=text("FALSE"),
                                               nullable=False, quote=False)
    issueMoney: Mapped[bool] = mapped_column("issuemoney", Boolean, default=False, server_default=text("FALSE"),
                                              nullable=False, quote=False)
    issueTime: Mapped[bool] = mapped_column("issuetime", Boolean, default=False, server_default=text("FALSE"),
                                             nullable=False, quote=False)
    issueSweating: Mapped[bool] = mapped_column("issuesweating", Boolean, default=False, server_default=text("FALSE"),
                                                 nullable=False, quote=False)
    issueComfort: Mapped[bool] = mapped_column("issuecomfort", Boolean, default=False, server_default=text("FALSE"),
                                                nullable=False, quote=False)
    issueDistance: Mapped[bool] = mapped_column("issuedistance", Boolean, default=False, server_default=text("FALSE"),
                                                 nullable=False, quote=False)
    issueOther: Mapped[str] = mapped_column("issueother", Text, default=None, server_default=text("NULL"),
                                             nullable=True, quote=False)

    # these improvements would make me more likely to cycle again
    improvementNone: Mapped[bool] = mapped_column("improvementnone", Boolean, default=False,
                                                  server_default=text("FALSE"),
                                                  nullable=False, quote=False)
    improvementCyclingPaths: Mapped[bool] = mapped_column("improvementcyclingpaths", Boolean, default=False, server_default=text("FALSE"),
                                                nullable=False, quote=False)
    improvementLights: Mapped[bool] = mapped_column("improvementlights", Boolean, default=False,
                                                          server_default=text("FALSE"),
                                                          nullable=False, quote=False)
    improvementSurface: Mapped[bool] = mapped_column("improvementsurface", Boolean, default=False,
                                                          server_default=text("FALSE"),
                                                          nullable=False, quote=False)
    improvementCleaner: Mapped[bool] = mapped_column("improvementcleaner", Boolean, default=False,
                                                          server_default=text("FALSE"),
                                                          nullable=False, quote=False)
    improvementOther: Mapped[str] = mapped_column("improvementother", Text, default=None,
                                                          server_default=text("NULL"),
                                                          nullable=True, quote=False)

    # if not stopped cycling, what is the alternative
    alternativeOwnBike: Mapped[bool] = mapped_column("alternativeownbike", Boolean, default=False, server_default=text("FALSE"),
                                               nullable=False, quote=False)
    alternativeShareFriendsFamily: Mapped[bool] = mapped_column("alternativesharefriendsfamily", Boolean, default=False,
                                                     server_default=text("FALSE"),
                                                     nullable=False, quote=False)
    alternativeAnotherBecycle: Mapped[bool] = mapped_column("alternativeanotherbecycle", Boolean, default=False,
                                                         server_default=text("FALSE"),
                                                         nullable=False, quote=False)
    alternativeOtherRental: Mapped[bool] = mapped_column("alternativeotherrental", Boolean, default=False,
                                                     server_default=text("FALSE"),
                                                     nullable=False, quote=False)
