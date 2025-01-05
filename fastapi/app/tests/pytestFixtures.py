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
def clients_temp() -> list[models.ClientTemp]:
    test_clients_temp = add_clients_temp(db=db)

    yield test_clients_temp

    db.query(models.ClientTemp).delete()
    db.commit()


@pytest.fixture
def client_logins(clients) -> list[models.ClientLogin]:
    test_client_logins = add_client_logins(db=db, clients=clients)

    yield test_client_logins

    db.query(models.ClientLogin).delete()
    db.commit()


@pytest.fixture
def client_logins_with_duplicate_clients(clients_with_duplicates) -> list[models.ClientLogin]:
    test_client_logins_with_duplicates = add_client_logins(db=db, clients=clients_with_duplicates)

    yield test_client_logins_with_duplicates

    db.query(models.ClientLogin).delete()
    db.commit()


@pytest.fixture
def client_logins_expired(clients) -> list[models.ClientLogin]:
    test_client_logins_expired = add_client_logins_expired(db=db, clients=clients)

    yield test_client_logins_expired

    db.query(models.ClientLogin).delete()
    db.commit()


@pytest.fixture
def clients() -> list[models.Client]:
    test_clients = add_clients(db=db)

    yield test_clients

    db.query(models.Client).delete()
    db.commit()


@pytest.fixture
def clients_with_duplicates() -> list[models.Client]:
    test_clients_with_duplicates = add_clients_with_duplicates(db=db)

    yield test_clients_with_duplicates

    db.query(models.Client).delete()
    db.commit()


@pytest.fixture
def detected_potential_client_duplicates(clients_with_duplicates) -> list[models.DetectedPotentialClientDuplicates]:
    test_detected_potential_client_duplicates = add_detected_potential_client_duplicates(db=db, clients=clients_with_duplicates)

    yield test_detected_potential_client_duplicates

    db.query(models.DetectedPotentialClientDuplicates).delete()
    db.commit()


@pytest.fixture
def bikes() -> list[models.Bike]:
    test_bikes = add_bikes(db=db)

    yield test_bikes

    db.query(models.Bike).delete()
    db.commit()


@pytest.fixture
def bikes_with_duplicates() -> list[models.Bike]:
    test_bikes_with_duplicates = add_bikes_with_duplicates(db=db)

    yield test_bikes_with_duplicates

    db.query(models.Bike).delete()
    db.commit()


@pytest.fixture
def detected_potential_bike_duplicates(bikes_with_duplicates) -> list[models.DetectedPotentialBikeDuplicates]:
    test_detected_potential_bike_duplicates = add_detected_potential_bike_duplicates(db=db, bikes=bikes_with_duplicates)

    yield test_detected_potential_bike_duplicates

    db.query(models.DetectedPotentialBikeDuplicates).delete()
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
def contracts_soon(users: list[models.User], bikes: list[models.Bike], clients: list[models.Client], contract_types: list[models.ContractType]) -> list[models.Contract]:
    test_contracts = add_contracts_test_reminders(db=db, users=users, bikes=bikes, clients=clients, contract_types=contract_types)

    yield test_contracts

    db.query(models.Contract).delete()
    db.commit()


@pytest.fixture
def contracts_with_duplicate_clients_and_bikes(users: list[models.User], bikes_with_duplicates: list[models.Bike], clients_with_duplicates: list[models.Client], contract_types: list[models.ContractType]) -> list[models.Contract]:
    test_contracts = add_contracts(db=db, users=users, bikes=bikes_with_duplicates, clients=clients_with_duplicates, contract_types=contract_types)

    yield test_contracts

    db.query(models.Contract).delete()
    db.commit()


@pytest.fixture
def paper_contracts(contracts: list[models.Contract]) -> list[models.PaperContract]:
    test_paper_contracts = add_paper_contracts(db=db, contracts=contracts)

    yield test_paper_contracts

    db.query(models.PaperContract).delete()
    db.commit()


@pytest.fixture
def appointment_types() -> list[models.AppointmentType]:
    test_appointment_types = add_appointment_types(db=db)

    yield test_appointment_types

    db.query(models.AppointmentType).delete()
    db.commit()


@pytest.fixture
def appointments(appointment_types: list[models.AppointmentType], clients: list[models.Client], appointment_general_settings: models.AppointmentGeneralSettings) -> list[models.Appointment]:
    test_appointments = add_appointments(db=db, clients=clients, appointment_types=appointment_types, appointment_general_settings=appointment_general_settings)

    yield test_appointments

    db.query(models.Appointment).delete()
    db.commit()


@pytest.fixture
def appointments_soon(appointment_types: list[models.AppointmentType], clients: list[models.Client], appointment_general_settings: models.AppointmentGeneralSettings):
    test_appointments_soon = add_appointments_test_reminders(db=db, clients=clients, appointment_types=appointment_types, appointment_general_settings=appointment_general_settings)

    yield test_appointments_soon

    db.query(models.Appointment).delete()
    db.commit()


@pytest.fixture
def appointments_with_client_duplicates(appointment_types: list[models.AppointmentType], clients_with_duplicates: list[models.Client], appointment_general_settings: models.AppointmentGeneralSettings) -> list[models.Appointment]:
    test_appointments = add_appointments(db=db, clients=clients_with_duplicates, appointment_types=appointment_types, appointment_general_settings=appointment_general_settings)

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
def closed_days(appointment_general_settings) -> list[models.ClosedDay]:
    test_closed_days = add_closed_days(db=db, appointment_general_settings=appointment_general_settings)

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
        access_token = auth.create_access_token(data={"sub": user.username})

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
        access_token = auth.create_access_token(data={"sub": str(client.id)})

        tokens.append(
            schemas.Token(
                access_token=access_token,
                token_type="bearer"
            )
        )

    return tokens


@pytest.fixture
def road_segments() -> list[models.RoadSegment]:
    test_road_segments = add_road_segments(db=db)

    yield test_road_segments

    db.query(models.RoadSegment).delete()
    db.commit()


@pytest.fixture
def road_segment_report_types() -> list[models.RoadSegmentReportType]:
    test_road_segment_report_types = add_road_segment_report_types(db=db)

    yield test_road_segment_report_types

    db.query(models.RoadSegmentReportType).delete()
    db.commit()


@pytest.fixture
def road_segment_reports(road_segments, road_segment_report_types) -> list[models.RoadSegmentReport]:
    test_road_segment_reports = add_road_segment_reports(db=db, road_segments=road_segments, road_segment_report_types=road_segment_report_types)

    yield test_road_segment_reports

    db.query(models.RoadSegmentReport).delete()
    db.commit()


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
def appointment_manager_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[1].access_token
    }


@pytest.fixture
def deposit_bearer_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[2].access_token
    }


@pytest.fixture
def treasurer_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[0].access_token
    }


@pytest.fixture
def client_auth_headers(client_auth_tokens) -> list[dict]:
    return [{"Authorization": "Bearer " + client_auth_token.access_token} for client_auth_token in client_auth_tokens]


@pytest.fixture
def expense_types() -> list[models.ExpenseType]:
    test_expense_types = add_expense_types(db=db)

    yield test_expense_types

    db.query(models.ExpenseType).delete()
    db.commit()


@pytest.fixture
def expense_receipts() -> list[models.ExpenseReceipt]:
    test_expense_receipts = add_expense_receipts(db=db)

    yield test_expense_receipts

    db.query(models.ExpenseReceipt).delete()
    db.commit()

@pytest.fixture
def expense_tags() -> list[models.ExpenseTag]:
    test_expense_tags = add_expense_tags(db=db)

    yield test_expense_tags

    db.query(models.ExpenseTag).delete()
    db.commit()


@pytest.fixture
def expenses(expense_types, expense_tags, users, expense_receipts) -> list[models.Expense]:
    test_expenses = add_expenses(db=db, users=users, expense_receipts=expense_receipts, expense_types=expense_types, expense_tags=expense_tags)

    yield test_expenses

    db.query(models.Expense).delete()
    db.commit()