from fastapi import APIRouter, Depends
import app.crud as crud
import app.schemas as schemas
from app.dependencies import get_db
from sqlalchemy.orm import Session


clients = APIRouter(
    tags=["clients"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not Found"}}
)


@clients.get("/clients")
async def get_clients(first_name: str = None, last_name: str = None, email_address: str = None,
                      db: Session = Depends(get_db)) -> list[schemas.Client]:
    return crud.get_clients(db=db, first_name=first_name, last_name=last_name, email_address=email_address)


@clients.post("/client")
async def post_client(client: schemas.ClientCreate, db: Session = Depends(get_db)) -> schemas.Client:
    return crud.post_client(db=db, client_to_create=client)
