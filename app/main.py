from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import app.routers as routers
import uvicorn
from app.dependencies import get_db
from app.database.db import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(dependencies=[Depends(get_db)])

origins = [
        "http://localhost:5173",
        "https://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(routers.clients)
app.include_router(routers.users)
app.include_router(routers.bikes)
app.include_router(routers.contracts)
app.include_router(routers.settings)
app.include_router(routers.appointments)
app.include_router(routers.deposit_exchanges)
app.include_router(routers.finances)
app.include_router(routers.public)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
