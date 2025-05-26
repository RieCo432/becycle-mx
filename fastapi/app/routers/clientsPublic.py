from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import app.crud as crud
import app.dependencies as dep
import app.schemas as schemas
from app import auth


public_clients = APIRouter(
    tags=["clients-public"],
    dependencies=[Depends(dep.get_db)],
    responses={404: {"description": "Not Found"}}
)


@public_clients.post("/public/clients/temp")
async def create_client_temp(
        client_data: schemas.ClientCreate,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.ClientTemp:

    client_temp = crud.post_client_temp(db=db, client_data=client_data)

    email_tasks.add_task(client_temp.send_email_verification_link)

    return client_temp


@public_clients.post("/public/clients/temp/verify")
async def verify_client_temp(
        client_temp_id: Annotated[UUID, Form()],
        verification_code: Annotated[str, Form()],
        db: Session = Depends(dep.get_db)) -> schemas.Token:

    client = crud.verify_client_temp(db=db, client_temp_id=client_temp_id, verification_code=verification_code)

    access_token = auth.create_access_token(data={"sub": str(client.id)})

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


@public_clients.get("/public/clients/login-code")
async def get_client_login_code(
        email_address: str,
        email_tasks: BackgroundTasks,
        db: Session = Depends(dep.get_db)) -> schemas.ClientPreAuth:

    client = crud.get_client_by_email(db=db, email_address=email_address.lower())

    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "There is no client associated with this email address."})

    client_login = crud.create_client_login_code(db=db, client=client)

    email_tasks.add_task(client_login.send_login_code)

    return schemas.ClientPreAuth(
        id=client.id
    )


@public_clients.post("/public/clients/token")
async def get_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(dep.get_db)) -> schemas.Token:

    client = crud.authenticate_client(db=db, client_id=UUID(form_data.username), login_code=form_data.password)

    access_token = auth.create_access_token(data={"sub": str(client.id)})

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )