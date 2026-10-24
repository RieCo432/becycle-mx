FROM python:3.11.17

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
COPY ./serve.sh /code/serve.sh

# Dump Python stack traces to stderr when a segfault/signal occurs
# (redundant with app/main.py's faulthandler.enable(), but covers processes
# that don't import the app, e.g. alembic)
ENV PYTHONFAULTHANDLER=1

ENV CLIENT_LOGIN_CODE_EXPIRE_MINUTES=60
# 1 DAY
ENV CLIENT_EMAIL_VERIFY_EXPIRE_MINUTES=1440
ENV CONTRACT_EXPIRE_MONTHS=6
ENV CONTRACT_GRACE_PERIOD_AFTER_EXPIRY_MONTHS=6
ENV CONTRACT_FORFEIT_AFTER_GRACE_PERIOD_MONTHS=6
ENV API_SECRET_ALGORITHM=HS256
# 1 WEEK
ENV ACCESS_TOKEN_EXPIRE_MINUTES=43200
ENV SMTP_SERVER=smtp.gmail.com
ENV SMTP_PORT=465
ENV API_HOST_ADDRESS=0.0.0.0
ENV API_HOST_PORT=8000

#
CMD sh -c "alembic upgrade head && exec sh /code/serve.sh"