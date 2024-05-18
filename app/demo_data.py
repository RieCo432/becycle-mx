import datetime
import os
import bcrypt
from dateutil.relativedelta import relativedelta
import app.models as models
from sqlalchemy.orm import Session


def delete_all(db: Session):
    db.query(models.RoadSegmentReport).delete()
    db.query(models.RoadSegmentReportType).delete()
    db.query(models.RoadSegment).delete()

    db.query(models.PaperContract).delete()
    db.query(models.Contract).delete()

    db.query(models.ExpenseReceipt).delete()
    db.query(models.Expense).delete()

    db.query(models.DepositExchange).delete()

    db.query(models.UserPresentationCard).delete()
    db.query(models.UserPhoto).delete()
    db.query(models.User).delete()

    db.query(models.DetectedPotentialBikeDuplicates).delete()
    db.query(models.Bike).delete()

    db.query(models.Appointment).delete()
    db.query(models.AppointmentType).delete()

    db.query(models.DetectedPotentialClientDuplicates).delete()
    db.query(models.ClientLogin).delete()
    db.query(models.Client).delete()

    db.query(models.Address).delete()
    db.query(models.ContractType).delete()
    db.query(models.PeriBecycleSurvey).delete()
    db.query(models.PostBecycleSurvey).delete()
    db.query(models.PreBecycleSurvey).delete()
    db.query(models.AppointmentGeneralSettings).delete()
    db.query(models.AppointmentConcurrencyLimit).delete()
    db.query(models.ClientTemp).delete()
    db.query(models.ClosedDay).delete()
    db.query(models.ExpenseType).delete()


def add_clients(db: Session) -> list[models.Client]:
    clients = [
        models.Client(
            firstName="alice",
            lastName="humphrey",
            emailAddress="alice.humphrey@example.com",
            preBecycleSurveyCompleted=False,
            periBecycleSurveyCompleted=False,
            postBecycleSurveyCompleted=False
        ),
        models.Client(
            firstName="bob",
            lastName="frank",
            emailAddress="bob.frank@example.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=False,
            postBecycleSurveyCompleted=False
        ),
        models.Client(
            firstName="charlie",
            lastName="maurice",
            emailAddress="charlie.maurice@example.com",
            preBecycleSurveyCompleted=False,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=False
        ),
        models.Client(
            firstName="debby",
            lastName="smith",
            emailAddress="daurice.smith@exmaple.com",
            preBecycleSurveyCompleted=False,
            periBecycleSurveyCompleted=False,
            postBecycleSurveyCompleted=True
        ),
        models.Client(
            firstName="alex",
            lastName="smith",
            emailAddress="alex.smith@example.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=True
        )
    ]

    db.add_all(clients)
    db.commit()

    return clients


def add_bikes(db: Session) -> list[models.Bike]:
    bikes = [
        models.Bike(make="apollo", model="skidmarks", colour="brown", decals=None, serialNumber="abcd1234"),
        models.Bike(make="apollo", model="excelle", colour="black", decals=None, serialNumber="abcd1256"),
        models.Bike(make="avigo", model="amethyst", colour="purple", decals=None, serialNumber="uvwx2345"),
        models.Bike(make="raleigh", model="chloe", colour="pink", decals=None, serialNumber="efgh5678"),
        models.Bike(make="raleigh", model="enigma", colour="blue", decals=None, serialNumber="mnop3456"),
        models.Bike(make="revolution", model="cuillin sport", colour="black", decals=None, serialNumber="qrst7890"),
        models.Bike(make="elephantbike", model="heavy af", colour="blue", decals=None, serialNumber="ijkl9012")
    ]

    db.add_all(bikes)
    db.commit()

    return bikes


def add_users(db: Session) -> list[models.User]:
    users = [
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
        models.User(
            username="nocarduser",
            password=bcrypt.hashpw("nocarduser1234", bcrypt.gensalt()),
            pin=None,
            admin=False,
            depositBearer=False,
            rentalChecker=False,
            appointmentManager=False,
            treasurer=False,
            softDeleted=False),
    ]

    db.add_all(users)
    db.commit()

    return users


def add_user_photos(db: Session, users: list[models.User]) -> list[models.UserPhoto]:
    user_photos = []
    current_directory = os.path.dirname(os.path.abspath(__file__))
    photos_directory = os.path.join(current_directory,"tests", "photos")
    for user in users[:5]:
        photo_path = os.path.join(photos_directory, user.username + ".jpg")
        with open(photo_path, "rb") as photo:
            user_photos.append(
                models.UserPhoto(
                    content=photo.read()
                )
            )

    db.add_all(user_photos)
    db.commit()

    return user_photos


def add_user_presentation_cards(db: Session, users: list[models.User], user_photos: list[models.UserPhoto]) -> list[models.UserPresentationCard]:
    user_presentation_cards = [
        models.UserPresentationCard(
            userId=users[0].id,
            name="Elaine",
            bio="This is Elaine's biography",
            photoContentType="image/jpeg",
            photoFileId=user_photos[0].id
        ),
        models.UserPresentationCard(
            userId=users[1].id,
            name="Freddy",
            bio="This is Freddy's biography",
            photoContentType="image/jpeg",
            photoFileId=user_photos[1].id
        ),
        models.UserPresentationCard(
            userId=users[2].id,
            name="George",
            bio="This is George's biography",
            photoContentType="image/jpeg",
            photoFileId=user_photos[2].id
        ),
        models.UserPresentationCard(
            userId=users[3].id,
            name="Daniel",
            bio="This is Daniel's biography",
            photoContentType="image/jpeg",
            photoFileId=user_photos[3].id
        ),
        models.UserPresentationCard(
            userId=users[4].id,
            name="Honey",
            bio="This is Honey's biography",
            photoContentType="image/jpeg",
            photoFileId=user_photos[4].id
        )
    ]

    db.add_all(user_presentation_cards)
    db.commit()

    return user_presentation_cards


def add_contracts(db: Session, users: list[models.User], clients: list[models.Client], bikes: list[models.Bike], contract_types: list[models.ContractType]) -> list[models.Contract]:
    contracts = [
        models.Contract(
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
            contractType=contract_types[0].id,
            notes="returned on time",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[1].id,
            bikeId=bikes[1].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=users[0].id,
            depositReturningUserId=users[0].id,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=20)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=14)).date(),
            returnedDate=(datetime.datetime.utcnow() - relativedelta(months=18)).date(),
            depositAmountCollected=40,
            depositAmountReturned=30,
            conditionOfBike="fair",
            contractType=contract_types[1].id,
            notes="returned very early",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[2].id,
            bikeId=bikes[2].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=7)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=1)).date(),
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="good",
            contractType=contract_types[0].id,
            notes="this should be expired",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[3].id,
            bikeId=bikes[3].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=3)).date(),
            endDate=(datetime.datetime.utcnow() + relativedelta(months=3)).date(),
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="fair",
            contractType=contract_types[2].id,
            notes="this one is open",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[4].id,
            bikeId=bikes[4].id,
            workingUserId=users[2].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=users[2].id,
            depositReturningUserId=users[2].id,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=10)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=4)).date(),
            returnedDate=(datetime.datetime.utcnow() - relativedelta(months=2)).date(),
            depositAmountCollected=40,
            depositAmountReturned=30,
            conditionOfBike="fair",
            contractType=contract_types[0].id,
            notes="returned late",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[2].id,
            bikeId=bikes[5].id,
            workingUserId=users[2].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=users[2].id,
            depositReturningUserId=users[2].id,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=16)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=10)).date(),
            returnedDate=(datetime.datetime.utcnow() - relativedelta(months=5)).date(),
            depositAmountCollected=40,
            depositAmountReturned=20,
            conditionOfBike="fair",
            contractType=contract_types[1].id,
            notes="returned very late",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(
            clientId=clients[4].id,
            bikeId=bikes[6].id,
            workingUserId=users[2].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=users[2].id,
            depositReturningUserId=users[2].id,
            startDate=(datetime.datetime.utcnow() - relativedelta(months=7)).date(),
            endDate=(datetime.datetime.utcnow() - relativedelta(months=1)).date(),
            returnedDate=(datetime.datetime.utcnow() - relativedelta(months=2)).date(),
            depositAmountCollected=40,
            depositAmountReturned=40,
            conditionOfBike="fair",
            contractType=contract_types[0].id,
            notes="returned on time",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        )
    ]

    db.add_all(contracts)
    db.commit()

    return contracts


def add_appointment_types(db: Session) -> list[models.AppointmentType]:
    appointment_types = [
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

    db.add_all(appointment_types)
    db.commit()

    return appointment_types


def add_appointments(db: Session, clients: list[models.Client], appointment_types: list[models.AppointmentType]) -> list[models.Appointment]:
    appointments = [
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

    db.add_all(appointments)
    db.commit()

    return appointments


def add_appointment_settings(db: Session) -> models.AppointmentGeneralSettings:
    appointment_settings = models.AppointmentGeneralSettings(
        openingDays=[0, 2],
        minBookAhead=2,
        maxBookAhead=30,
        slotDuration=15
    )

    db.add(appointment_settings)
    db.commit()

    return appointment_settings


def add_appointment_concurrency_limits(db: Session) -> list[models.AppointmentConcurrencyLimit]:
    appointment_concurrency_limits = [
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

    db.add_all(appointment_concurrency_limits)
    db.commit()

    return appointment_concurrency_limits


def add_address(db: Session) -> models.Address:
    address = models.Address(
        number="21-23",
        street="High Street",
        postcode="AB24 3EE",
        city="Aberdeen"
    )

    db.add(address)
    db.commit()

    return address


def add_closed_days(db: Session) -> list[models.ClosedDay]:
    closed_days = [
        models.ClosedDay(
            date=datetime.datetime.utcnow().date() + relativedelta(days=7),
            note="Workshop Day"
        ),
        models.ClosedDay(
            date=datetime.datetime.utcnow().date() + relativedelta(days=28),
            note="Workshop Day 2"
        ),
    ]

    db.add_all(closed_days)
    db.commit()

    return closed_days


def add_deposit_exchanges(db: Session, users: list[models.User]) -> list[models.DepositExchange]:
    deposit_exchanges = [
        models.DepositExchange(
            amount=80,
            fromUserId=users[2].id,
            toUserId=users[0].id,
            date=(datetime.datetime.utcnow().date() - relativedelta(months=3))
        ),
        models.DepositExchange(
            amount=10,
            fromUserId=users[0].id,
            toUserId=users[2].id,
            date=(datetime.datetime.utcnow().date() - relativedelta(months=10))
        )
    ]

    db.add_all(deposit_exchanges)
    db.commit()

    return deposit_exchanges


def add_expense_types(db: Session) -> list[models.ExpenseType]:
    expense_types = [
        models.ExpenseType(
            id="consumabled",
            description="GT-85, Oil"
        ),
        models.ExpenseType(
            id="merchandise",
            description="Items to be sold"
        ),
        models.ExpenseType(
            id="cash",
            description="Cash from safe"
        )
    ]

    db.add_all(expense_types)
    db.commit()

    return expense_types


def add_contract_types(db: Session) -> list[models.ContractType]:
    contract_types = [
        models.ContractType(
            id="standard"
        ),
        models.ContractType(
            id="refugee"
        ),
        models.ContractType(
            id="kids"
        )
    ]

    db.add_all(contract_types)
    db.commit()

    return contract_types


if __name__ == "__main__":
    from app.database.db import Base, engine, SessionLocal

    Base.metadata.create_all(bind=engine)
    demo_db = SessionLocal()

    delete_all(db=demo_db)

    demo_users = add_users(db=demo_db)
    demo_bikes = add_bikes(db=demo_db)
    demo_clients = add_clients(db=demo_db)
    demo_user_photos = add_user_photos(db=demo_db, users=demo_users)
    demo_user_presentation_cards = add_user_presentation_cards(db=demo_db, users=demo_users, user_photos=demo_user_photos)
    demo_contract_types = add_contract_types(db=demo_db)
    demo_contracts = add_contracts(db=demo_db, users=demo_users, clients=demo_clients, bikes=demo_bikes, contract_types=demo_contract_types)
    demo_appointment_types = add_appointment_types(db=demo_db)
    demo_appointments = add_appointments(db=demo_db, appointment_types=demo_appointment_types, clients=demo_clients)
    demo_appointment_general_settings = add_appointment_settings(db=demo_db)
    demo_appointment_concurrency_limits = add_appointment_concurrency_limits(db=demo_db)
    demo_address = add_address(db=demo_db)
    demo_closed_days = add_closed_days(db=demo_db)
    demo_deposit_exchanges = add_deposit_exchanges(db=demo_db, users=demo_users)
    demo_expense_types = add_expense_types(db=demo_db)