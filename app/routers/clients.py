from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
import app.models as models
import app.crud as crud
import app.schemas as schemas
import app.dependencies as dep
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated
from app import auth
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES


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


@clients.get("/clients/email-address-suggestions", dependencies=[Depends(dep.get_current_active_user)])
async def get_client_email_address_suggestions(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> list[str]:
    return crud.get_similar_email_addresses(email_address=email_address, db=db)


@clients.post("/client", dependencies=[Depends(dep.get_current_active_user)])
async def create_client(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    return crud.post_client(db=db, client_data=client_data)


@clients.post("/client/temp")
async def create_client_temp(
        client_data: schemas.ClientCreate,
        db: Session = Depends(dep.get_db)) -> schemas.ClientTemp:

    client_temp = crud.post_client_temp(db=db, client_data=client_data)

    client_temp.send_email_verification_link()

    return client_temp


@clients.post("/client/temp/verify")
async def verify_client_temp(
        client_temp_id: Annotated[UUID, Form()],
        verification_code: Annotated[str, Form()],
        db: Session = Depends(dep.get_db)) -> schemas.Client:

    if client_temp_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No client ID provided."})
    if verification_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "No verification code provided."})

    client = crud.verify_client_temp(db=db, client_temp_id=client_temp_id, verification_code=verification_code)

    return client


@clients.get("/client/login-code")
async def get_client_login_code(
        email_address: str,
        db: Session = Depends(dep.get_db)) -> schemas.ClientPreAuth:

    client = crud.get_client_by_email(db=db, email_address=email_address)

    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "There is no client associated with this email address."})

    # TODO: this somehow always generates the same code and expiry datetime. Needs fixed
    client_login = crud.create_client_login_code(db=db, client=client)

    client_login.send_login_code()

    return schemas.ClientPreAuth(
        id=client.id
    )


@clients.post("/clients/token")
async def get_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)) -> schemas.Token:

    client = crud.authenticate_client(db=db, client_id=UUID(form_data.username), login_code=form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": str(client.id)}, expires_delta=access_token_expires)

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


@clients.get("/clients/me")
async def get_client_me(client: Annotated[models.Client, Depends(dep.get_current_client)]) -> schemas.Client:

    return client


