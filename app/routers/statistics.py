from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
import os


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


statistics = APIRouter(
    tags=["statistics"],
    responses={404: {"description": "Not Found"}}
)


@statistics.get("/statistics/users/leaderboard", dependencies=[Depends(dep.get_current_active_user)])
async def get_user_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.UserLeaderboard]:
    leaderboard = crud.get_user_leaderboard(db=db)

    return leaderboard


@statistics.get("/statistics/clients/leaderboard", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_leaderboard(
        db: Session = Depends(dep.get_db)
) -> list[schemas.ClientLeaderboard]:
    leaderboard = crud.get_client_leaderboard(db=db)

    return leaderboard
