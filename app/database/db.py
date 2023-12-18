from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

SQLALCHEMY_DATABASE_URL = url = URL.create(
    drivername="postgresql",
    username="becycleAdmin",
    password="drivetrain",
    host="localhost",
    database="becycledb"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

