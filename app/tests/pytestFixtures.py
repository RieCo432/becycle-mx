import pytest
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from app import auth
from app.demo_data import *
from app.database.db import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

delete_all(db=db)


@pytest.fixture
def clients() -> list[models.Client]:
    test_clients = add_clients(db=db)

    yield test_clients

    db.query(models.Client).delete()
    db.commit()


@pytest.fixture
def bikes() -> list[models.Bike]:
    test_bikes = add_bikes(db=db)

    yield test_bikes

    db.query(models.Bike).delete()
    db.commit()


@pytest.fixture
def users() -> list[models.User]:
    test_users = add_users(db=db)

    yield test_users

    db.query(models.User).delete()
    db.commit()


@pytest.fixture
def user_photos(users) -> list[models.UserPhoto]:
    test_user_photos = add_user_photos(db=db, users=users)

    yield test_user_photos

    db.query(models.UserPhoto).delete()
    db.commit()


@pytest.fixture
def user_presentation_cards(users: list[models.User], user_photos: list[models.UserPhoto]) -> list[models.UserPresentationCard]:
    test_user_presentation_cards = add_user_presentation_cards(db=db, users=users, user_photos=user_photos)

    yield test_user_presentation_cards

    db.query(models.UserPresentationCard).delete()
    db.commit()


@pytest.fixture
def contract_types() -> list[models.ContractType]:
    test_contract_types = add_contract_types(db=db)

    yield test_contract_types

    db.query(models.ContractType).delete()
    db.commit()


@pytest.fixture
def contracts(users: list[models.User], bikes: list[models.Bike], clients: list[models.Client], contract_types: list[models.ContractType]) -> list[models.Contract]:
    test_contracts = add_contracts(db=db, users=users, bikes=bikes, clients=clients, contract_types=contract_types)

    yield test_contracts

    db.query(models.Contract).delete()
    db.commit()


@pytest.fixture
def appointment_types() -> list[models.AppointmentType]:
    test_appointment_types = add_appointment_types(db=db)

    yield test_appointment_types

    db.query(models.AppointmentType).delete()
    db.commit()


@pytest.fixture
def appointments(appointment_types: list[models.AppointmentType], clients: list[models.Client]) -> list[models.Appointment]:
    test_appointments = add_appointments(db=db, clients=clients, appointment_types=appointment_types)

    yield test_appointments

    db.query(models.Appointment).delete()
    db.commit()


@pytest.fixture
def appointment_general_settings() -> models.AppointmentGeneralSettings:
    test_appointment_settings = add_appointment_settings(db=db)

    yield test_appointment_settings

    db.query(models.AppointmentGeneralSettings).delete()
    db.commit()


@pytest.fixture
def appointment_concurrency_limits() -> list[models.AppointmentConcurrencyLimit]:
    test_concurrency_settings = add_appointment_concurrency_limits(db=db)

    yield test_concurrency_settings

    db.query(models.AppointmentConcurrencyLimit).delete()
    db.commit()


@pytest.fixture
def address() -> models.Address:
    test_address = add_address(db=db)

    yield test_address

    db.query(models.Address).delete()
    db.commit()


@pytest.fixture
def closed_days() -> list[models.ClosedDay]:
    test_closed_days = add_closed_days(db=db)

    yield test_closed_days

    db.query(models.ClosedDay).delete()
    db.commit()


@pytest.fixture
def deposit_exchanges(users) -> list[models.DepositExchange]:
    test_deposit_exchanges = add_deposit_exchanges(db=db, users=users)

    yield test_deposit_exchanges

    db.query(models.DepositExchange).delete()
    db.commit()


@pytest.fixture
def user_auth_tokens(users) -> list[schemas.Token]:
    tokens = []
    for user in users:
        access_token_expires = datetime.timedelta(minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
        access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

        tokens.append(
            schemas.Token(
                access_token=access_token,
                token_type="bearer"
            )
        )

    return tokens


@pytest.fixture
def client_auth_tokens(clients) -> list[schemas.Token]:
    tokens = []
    for client in clients:
        access_token_expires = datetime.timedelta(minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
        access_token = auth.create_access_token(data={"sub": str(client.id)}, expires_delta=access_token_expires)

        tokens.append(
            schemas.Token(
                access_token=access_token,
                token_type="bearer"
            )
        )

    return tokens


@pytest.fixture
def normal_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[3].access_token
    }


@pytest.fixture
def admin_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[0].access_token
    }


@pytest.fixture
def deposit_bearer_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[2].access_token
    }


@pytest.fixture
def client_auth_headers(client_auth_tokens) -> list[dict]:
    return [{"Authorization": "Bearer " + client_auth_token.access_token} for client_auth_token in client_auth_tokens]
