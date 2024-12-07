from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def create_pre_becycle_survey_entry(db: Session, survey_answers: schemas.PreBecycleSurvey) -> None:
    survey_entry = models.PreBecycleSurvey(**survey_answers.model_dump())

    db.add(survey_entry)
    db.commit()


def create_peri_becycle_survey_entry(db: Session, survey_answers: schemas.PeriBecycleSurvey) -> None:
    survey_entry = models.PeriBecycleSurvey(**survey_answers.model_dump())

    db.add(survey_entry)
    db.commit()


def create_post_becycle_survey_entry(db: Session, survey_answers: schemas.PostBecycleSurvey) -> None:
    survey_entry = models.PostBecycleSurvey(**survey_answers.model_dump())

    db.add(survey_entry)
    db.commit()
