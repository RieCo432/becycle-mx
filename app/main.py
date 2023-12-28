from fastapi import FastAPI, Depends
import app.routers as routers
import uvicorn
from app.dependencies import get_db
from app.database.db import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(dependencies=[Depends(get_db)])

app.include_router(routers.clients)
app.include_router(routers.users)
app.include_router(routers.bikes)
app.include_router(routers.contracts)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
