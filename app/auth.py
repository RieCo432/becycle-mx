import os
from datetime import datetime, timedelta

from jose import jwt

API_SECRET = os.environ['API_SECRET']
API_SECRET_ALGORITHM = os.environ['API_SECRET_ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET, algorithm=API_SECRET_ALGORITHM)
    return encoded_jwt


def create_expired_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() - timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET, algorithm=API_SECRET_ALGORITHM)
    return encoded_jwt
