from fastapi import APIRouter, Depends, Body, HTTPException, status
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated

clients = APIRouter(
    tags=["clients"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@clients.get("/clients", dependencies=[Depends(dep.get_current_active_user)])
async def get_clients(
            first_name: str = None,
            last_name: str = None,
            email_address: str = None,
            db: Session = Depends(dep.get_db)) -> list[schemas.Client]:
    return crud.get_clients(db=db, first_name=first_name, last_name=last_name, email_address=email_address)


@clients.post("/client", dependencies=[Depends(dep.get_current_active_user)])
async def create_client(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    return crud.post_client(db=db, client_data=client_data)


@clients.post("/client/temp")
async def create_client_temp(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.ClientTemp:

    return crud.post_client_temp(db=db, client_data=client_data)


@clients.put("/client/temp/verify")
async def verify_client_temp(
        client_temp_id: UUID | None = None,
        verification_code: Annotated[str, None] = Body("verification_code"),
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    if client_temp_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No client ID provided."})
    if verification_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No verification code provided."})

    return crud.verify_client_temp(db=db, client_temp_id=client_temp_id, verification_code=verification_code)

