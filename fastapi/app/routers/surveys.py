from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.models as models
import app.schemas as schemas

surveys = APIRouter(
    tags=["surveys"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@surveys.post("/surveys/pre-becycle")
async def post_pre_becycle_survey(survey_answers: schemas.PreBecycleSurvey,
                                  client: models.Client = Depends(dep.get_current_client),
                                  db: Session = Depends(dep.get_db)):
    if client.preBecycleSurveyCompleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"description": "You have already completed this survey"})

    crud.create_pre_becycle_survey_entry(db=db, survey_answers=survey_answers)
    client.preBecycleSurveyCompleted = True
    db.commit()


@surveys.post("/surveys/peri-becycle")
async def post_peri_becycle_survey(survey_answers: schemas.PeriBecycleSurvey,
                                   client: models.Client = Depends(dep.get_current_client),
                                   db: Session = Depends(dep.get_db)):
    if client.periBecycleSurveyCompleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"description": "You have already completed this survey"})

    crud.create_peri_becycle_survey_entry(db=db, survey_answers=survey_answers)
    client.periBecycleSurveyCompleted = True
    db.commit()


@surveys.post("/surveys/post-becycle")
async def post_post_becycle_survey(survey_answers: schemas.PostBecycleSurvey,
                                   client: models.Client = Depends(dep.get_current_client),
                                   db: Session = Depends(dep.get_db)):
    if client.postBecycleSurveyCompleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"description": "You have already completed this survey"})

    crud.create_post_becycle_survey_entry(db=db, survey_answers=survey_answers)
    client.postBecycleSurveyCompleted = True
    db.commit()
