import datetime
import os
import pytest
import bcrypt
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from app import auth
from app.database.db import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def clear_database():
    db.query(models.Address).delete()
    db.query(models.ContractType).delete()
    db.query(models.DetectedPotentialBikeDuplicates).delete()
    db.query(models.DetectedPotentialClientDuplicates).delete()
    db.query(models.Expense).delete()
    db.query(models.ExpenseReceipt).delete()
    db.query(models.PeriBecycleSurvey).delete()
    db.query(models.PostBecycleSurvey).delete()
    db.query(models.PreBecycleSurvey).delete()
    db.query(models.RoadSegmentReport).delete()
    db.query(models.RoadSegment).delete()
    db.query(models.PaperContract).delete()
    db.query(models.Contract).delete()
    db.query(models.Bike).delete()
    db.query(models.DepositExchange).delete()
    db.query(models.Appointment).delete()
    db.query(models.AppointmentGeneralSettings).delete()
    db.query(models.AppointmentType).delete()
    db.query(models.AppointmentConcurrencyLimit).delete()
    db.query(models.ClientTemp).delete()
    db.query(models.ClientLogin).delete()
    db.query(models.Client).delete()
    db.query(models.ClosedDay).delete()
    db.query(models.UserPresentationCard).delete()
    db.query(models.UserPhoto).delete()
    db.query(models.User).delete()
    db.query(models.Expense).delete()
    db.query(models.ExpenseReceipt).delete()


@pytest.fixture
def clients() -> list[models.Client]:
    test_clients = [
        models.Client(firstName="alice", lastName="humphrey", emailAddress="alice.humphrey@example.com"),
        models.Client(firstName="bob", lastName="frank", emailAddress="bob.frank@example.com"),
        models.Client(firstName="charlie", lastName="maurice", emailAddress="charlie.maurice@example.com"),
        models.Client(firstName="debby", lastName="smith", emailAddress="daurice.smith@exmaple.com"),
        models.Client(firstName="alex", lastName="smith", emailAddress="alex.smith@example.com")
    ]

    db.add_all(test_clients)
    db.commit()

    yield test_clients

    db.query(models.Client).delete()
    db.commit()


@pytest.fixture
def bikes() -> list[models.Bike]:

    test_bikes = [
        models.Bike(make="apollo", model="skidmarks", colour="brown", decals=None, serialNumber="abcd1234"),
        models.Bike(make="apollo", model="excelle", colour="black", decals=None, serialNumber="abcd1256"),
        models.Bike(make="avigo", model="amethyst", colour="purple", decals=None, serialNumber="uvwx2345"),
        models.Bike(make="raleigh", model="chloe", colour="pink", decals=None, serialNumber="efgh5678"),
        models.Bike(make="raleigh", model="enigma", colour="blue", decals=None, serialNumber="mnop3456"),
        models.Bike(make="revolution", model="cuillin sport", colour="black", decals=None, serialNumber="qrst7890"),
        models.Bike(make="elephantbike", model="heavy af", colour="blue", decals=None, serialNumber="ijkl9012")
    ]

    db.add_all(test_bikes)
    db.commit()

    yield test_bikes

    db.query(models.Bike).delete()
    db.commit()


@pytest.fixture
def users() -> list[models.User]:
    test_users = [
        models.User(
            username="elaine",
            password=bcrypt.hashpw("elaine1234", bcrypt.gensalt()),
            pin=bcrypt.hashpw("0000", bcrypt.gensalt()),
            admin=True,
            depositBearer=True,
            rentalChecker=True,
            appointmentManager=True,
            treasurer=True,
            softDeleted=False),

        models.User(
            username="freddy",
            password=bcrypt.hashpw("freddy1234", bcrypt.gensalt()),
            pin=bcrypt.hashpw("1111", bcrypt.gensalt()),
            admin=False,
            depositBearer=False,
            rentalChecker=True,
            appointmentManager=True,
            treasurer=False,
            softDeleted=False),

        models.User(
            username="george",
            password=bcrypt.hashpw("george1234", bcrypt.gensalt()),
            pin=bcrypt.hashpw("2222", bcrypt.gensalt()),
            admin=False,
            depositBearer=True,
            rentalChecker=False,
            appointmentManager=False,
            treasurer=False,
            softDeleted=False),

        models.User(
            username="daniel",
            password=bcrypt.hashpw("daniel1234", bcrypt.gensalt()),
            pin=bcrypt.hashpw("3333", bcrypt.gensalt()),
            admin=False,
            depositBearer=False,
            rentalChecker=False,
            appointmentManager=False,
            treasurer=False,
            softDeleted=False),

        models.User(
            username="honey",
            password=bcrypt.hashpw("honey1234", bcrypt.gensalt()),
            pin=bcrypt.hashpw("4444", bcrypt.gensalt()),
            admin=False,
            depositBearer=False,
            rentalChecker=False,
            appointmentManager=False,
            treasurer=False,
            softDeleted=True),
    ]

    db.add_all(test_users)
    db.commit()

    yield test_users

    db.query(models.User).delete()
    db.commit()


@pytest.fixture
def user_presentation_cards(users: list[models.User]) -> list[models.UserPresentationCard]:
    test_user_presentation_cards = [
        models.UserPresentationCard(
            userId=users[0].id,
            name="Elaine",
            bio="This is Elaine's biography"
        ),
        models.UserPresentationCard(
            userId=users[1].id,
            name="Freddy",
            bio="This is Freddy's biography"
        ),
        models.UserPresentationCard(
            userId=users[2].id,
            name="George",
            bio="This is George's biography"
        ),
        models.UserPresentationCard(
            userId=users[3].id,
            name="Honey",
            bio="This is Honey's biography"
        )
    ]

    db.add_all(test_user_presentation_cards)
    db.commit()

    yield test_user_presentation_cards

    db.query(models.UserPresentationCard).delete()
    db.commit()


@pytest.fixture
def contracts(users: list[models.User], bikes: list[models.Bike], clients: list[models.Client]) -> list[models.Contract]:
    test_contracts = [models.Contract(
            clientId=clients[0].id,
            bikeId=bikes[0].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=users[0].id,
            depositReturningUserId=users[0].id,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=15)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=9)).date(),
            returnedDate=(datetime.datetime.utcnow() - relativedelta(months=10)).date(),
            depositAmountCollected=40,
            depositAmountReturned=30,
            conditionOfBike="fair",
            contractType="standard",
            notes="returned on time",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[0].id,
            bikeId=bikes[1].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=7)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=1)).date(),
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="good",
            contractType="standard",
            notes="this should be expired",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[0].id,
            bikeId=bikes[2].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=3)).date(),
            endDate=(datetime.datetime.utcnow() + relativedelta(months=3)).date(),
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="fair",
            contractType="standard",
            notes="this one is open",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        )
    ]

    db.add_all(test_contracts)
    db.commit()

    yield test_contracts

    db.query(models.Contract).delete()
    db.commit()


@pytest.fixture
def appointment_types() -> list[models.AppointmentType]:
    test_appointment_types = [
        models.AppointmentType(
            id="lend",
            active=True,
            title="Lending",
            description="You know what this is",
            duration=120
        ),
        models.AppointmentType(
            id="mrep",
            active=True,
            title="Medium Repair",
            description="You know what this is",
            duration=60
        )
    ]

    db.add_all(test_appointment_types)
    db.commit()

    yield test_appointment_types

    db.query(models.AppointmentType).delete()
    db.commit()


@pytest.fixture
def appointments(appointment_types: list[models.AppointmentType], clients: list[models.Client]) -> list[models.Appointment]:
    test_appointments = [
        models.Appointment(
            clientId=clients[1].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine((datetime.datetime.utcnow() - relativedelta(month=2)).date(), datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine((datetime.datetime.utcnow() - relativedelta(month=2)).date(), datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[3].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine((datetime.datetime.utcnow() + relativedelta(days=2)).date(), datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine((datetime.datetime.utcnow() + relativedelta(days=2)).date(), datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        )
    ]

    db.add_all(test_appointments)
    db.commit()

    yield test_appointments

    db.query(models.Appointment).delete()
    db.commit()


@pytest.fixture
def appointment_general_settings() -> models.AppointmentGeneralSettings:
    test_appointment_settings = models.AppointmentGeneralSettings(
            openingDays=[0, 2],
            minBookAhead=2,
            maxBookAhead=30,
            slotDuration=15
        )

    db.add(test_appointment_settings)
    db.commit()

    yield test_appointment_settings

    db.query(models.AppointmentGeneralSettings).delete()
    db.commit()


@pytest.fixture
def appointment_concurrency_limits() -> list[models.AppointmentConcurrencyLimit]:
    test_concurrency_settings = [
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=0, minute=0),
            maxConcurrent=0
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=16, minute=15),
            maxConcurrent=2
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=17, minute=30),
            maxConcurrent=4
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=19, minute=45),
            maxConcurrent=0
        )
    ]

    db.add_all(test_concurrency_settings)
    db.commit()

    yield test_concurrency_settings

    db.query(models.AppointmentConcurrencyLimit).delete()
    db.commit()


@pytest.fixture
def address() -> models.Address:
    test_address = models.Address(
        number="21-23",
        street="High Street",
        postcode="AB24 3EE",
        city="Aberdeen"
    )

    db.add(test_address)
    db.commit()

    yield test_address

    db.query(models.Address).delete()
    db.commit()


@pytest.fixture
def closed_days() -> list[models.ClosedDay]:
    test_closed_days = [
        models.ClosedDay(
            date=datetime.datetime.utcnow().date() + relativedelta(days=7),
            note="Workshop Day"
        ),
        models.ClosedDay(
            date=datetime.datetime.utcnow().date() + relativedelta(days=28),
            note="Workshop Day 2"
        ),

    ]

    db.add_all(test_closed_days)
    db.commit()

    yield test_closed_days

    db.query(models.ClosedDay).delete()
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
                token_type= "bearer"
            )
        )

    return tokens


@pytest.fixture
def normal_user_auth_header(user_auth_tokens) -> dict:
    return {
        "Authorization": "Bearer " + user_auth_tokens[3].access_token
    }