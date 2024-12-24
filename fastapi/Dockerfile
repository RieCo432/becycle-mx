FROM python:3.11.7

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic
COPY ./app /code/app

ENV CLIENT_LOGIN_CODE_EXPIRE_MINUTES=60
# 1 DAY
ENV CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES=1440
ENV CONTRACT_EXPIRE_MONTHS=6
ENV API_SECRET_ALGORITHM=HS256
# 1 WEEK
ENV ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENV SMTP_SERVER=smtp.gmail.com
ENV SMTP_PORT=465
ENV API_HOST_ADDRESS=0.0.0.0
ENV API_HOST_PORT=8000

#
CMD alembic upgrade head && uvicorn app.main:app --host ${API_HOST_ADDRESS} --port ${API_HOST_PORT}