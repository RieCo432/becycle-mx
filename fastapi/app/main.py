import os

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

import app.routers as routers
from app.database.db import engine, Base, SessionLocal
from app.dependencies import get_db
import app.crud as crud

if os.environ["PRODUCTION"] == "true":
    app = FastAPI(dependencies=[Depends(get_db)], docs_url=None, redoc_url=None)
else:
    app = FastAPI(dependencies=[Depends(get_db)])

origins = [
    os.environ['CORS_ALLOW_ORIGIN']
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if os.environ["PRODUCTION"] == "true" else "*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(routers.clients_me)
app.include_router(routers.public_clients)
app.include_router(routers.appointments_public)
app.include_router(routers.users_public)
app.include_router(routers.public)
app.include_router(routers.clients)
app.include_router(routers.users)
app.include_router(routers.bikes)
app.include_router(routers.contracts)
app.include_router(routers.settings)
app.include_router(routers.appointments)
app.include_router(routers.deposit_exchanges)
app.include_router(routers.finances)
app.include_router(routers.statistics)
# app.include_router(routers.maps)
# app.include_router(routers.surveys)
app.include_router(routers.admin)
app.include_router(routers.expenses)
app.include_router(routers.groups)



if os.environ["PRODUCTION"] == "true":
    db = SessionLocal()
    crud.send_expiry_emails(db=db)
    crud.send_appointment_reminders(db=db)
    db.close()

db = SessionLocal()
crud.ensure_all_permissions_exist(db=db, routes=[route for route in app.routes if isinstance(route, APIRoute)])
crud.fully_prune_tree(db=db)
db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
