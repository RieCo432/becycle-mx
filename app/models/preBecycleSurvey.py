from sqlalchemy import text, Boolean, Text, Integer, UUID
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from app.database.db import Base


class PreBecycleSurvey(Base):
    __tablename__ = "prebecyclesurvey"

    id: Mapped[UUID] = mapped_column("id", UUID, primary_key=True, default=uuid4, server_default=text("uuid_generate_v4()"), index=True, quote=False)

    # hurdles
    hurdleSafety: Mapped[bool] = mapped_column("hurdleSafety", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleMoney: Mapped[bool] = mapped_column("hurdleMoney", Boolean, default=False, server_default=text("FALSE"),
                                             nullable=False, quote=False)
    hurdleTime: Mapped[bool] = mapped_column("hurdleTime", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleSweating: Mapped[bool] = mapped_column("hurdleSweating", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleComfort: Mapped[bool] = mapped_column("hurdleComfort", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleDistance: Mapped[bool] = mapped_column("hurdleDistance", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    hurdleOther: Mapped[str] = mapped_column("hurdleOther", Text, default=None, server_default=text("NULL"), nullable=True, quote=False)

    # motivation
    motivationMoney: Mapped[bool] = mapped_column("motivationMoney", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    motivationHealth: Mapped[bool] = mapped_column("motivationHealth", Boolean, default=False, server_default=text("FALSE"), nullable=False, quote=False)
    motivationEnvironmental: Mapped[bool] = mapped_column("motivationEnvironmental", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                             quote=False)
    motivationOther: Mapped[str] = mapped_column("motivationOther", Text, default=None, server_default=text("NULL"), nullable=True,
                                             quote=False)

    # options considered
    consideredNewOnline: Mapped[bool] = mapped_column("consideredNewOnline", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    consideredNewShop: Mapped[bool] = mapped_column("consideredNewShop", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredUsed: Mapped[bool] = mapped_column("consideredUsed", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredLendingPrivate: Mapped[bool] = mapped_column("consideredLendingPrivate", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredLendingBecycle: Mapped[bool] = mapped_column("consideredLendingBecycle", Boolean, default=False,
                                                      server_default=text("FALSE"), nullable=False,
                                                      quote=False)
    consideredOther: Mapped[str] = mapped_column("consideredOther", Text, default=None,
                                                      server_default=text("NULL"), nullable=True,
                                                      quote=False)

    # training
    trainingExperienceMonths: Mapped[int] = mapped_column("trainingExperience", Integer, nullable=False, quote=False)
    trainingFormal: Mapped[bool] = mapped_column("trainingFormal", Boolean, default=False, server_default=text("FALSE"), nullable=False,
                                          quote=False)
    trainingConfidence: Mapped[int] = mapped_column("trainingConfidence", Integer, nullable=False, quote=False)
    trainingRules: Mapped[bool] = mapped_column("trainingRules", Boolean, default=False, server_default=text("FALSE"),
                                                 nullable=False,
                                                 quote=False)
    trainingDriver: Mapped[bool] = mapped_column("trainingDriver", Boolean, default=False, server_default=text("FALSE"),
                                                nullable=False,
                                                quote=False)

    # interest
    interestMaintenanceDesired: Mapped[int] = mapped_column("interestMaintenanceDesired", Integer, nullable=False, quote=False)
    interestMaintenanceCurrent: Mapped[int] = mapped_column("interestMaintenanceCurrent", Integer, nullable=False, quote=False)




