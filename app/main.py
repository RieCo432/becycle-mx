from fastapi import FastAPI, Depends
from app.routers import clients
import uvicorn
from app.dependencies import get_db
from app.database.db import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(dependencies=[Depends(get_db)])
app.include_router(clients.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)