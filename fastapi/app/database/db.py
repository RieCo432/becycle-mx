import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DATABASE = os.environ['POSTGRES_DB']
POSTGRES_HOST = os.environ['POSTGRES_HOST']


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    database=POSTGRES_DATABASE,
    host=POSTGRES_HOST
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=40, pool_timeout=5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

