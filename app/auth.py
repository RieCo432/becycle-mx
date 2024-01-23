from datetime import datetime, timedelta
import os
from jose import jwt


API_SECRET = os.environ['API_SECRET']
API_SECRET_ALGORITHM = os.environ['API_SECRET_ALGORITHM']


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET, algorithm=API_SECRET_ALGORITHM)
    return encoded_jwt
