import datetime
import os
import bcrypt
from dateutil.relativedelta import relativedelta
from fastapi.routing import APIRoute
from scipy.signal import cascade
from sqlalchemy import select

import app.models as models
from sqlalchemy.orm import Session


today = datetime.datetime.utcnow().date()
one_quarter_ago = (today - relativedelta(months=3))
two_quarter_ago = (one_quarter_ago - relativedelta(months=3))
three_quarter_ago = (two_quarter_ago - relativedelta(months=3))
four_quarter_ago = (three_quarter_ago - relativedelta(months=3))
five_quarter_ago = (four_quarter_ago - relativedelta(months=3))
six_quarter_ago = (five_quarter_ago - relativedelta(months=3))


def delete_all(db: Session):
    db.query(models.RoadSegmentReport).delete()
    db.query(models.RoadSegmentReportType).delete()
    db.query(models.RoadSegment).delete()

    db.query(models.ContractDraft).delete()

    db.query(models.CrimeReport).delete()
    db.query(models.PaperContract).delete()
    db.query(models.Contract).delete()

    db.query(models.Expense).delete()
    db.query(models.ExpenseReceipt).delete()

    db.query(models.DepositExchange).delete()

    for g in db.scalars(select(models.Group)):
        [g.users.remove(gu) for gu in g.users]
        [g.permissions.remove(gp) for gp in g.permissions]

    db.commit()
    db.query(models.Group).delete()

    for u in db.scalars(select(models.User)):
        [u.permissions.remove(p) for p in u.permissions]


    db.query(models.Permission).delete()

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
    db.query(models.ExpenseTag).delete()


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
            emailAddress="debby.smith@exmaple.com",
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


def add_clients_with_duplicates(db: Session) -> list[models.Client]:
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
            firstName="alex",
            lastName="smith",
            emailAddress="a.smith@example.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=False,
            postBecycleSurveyCompleted=False
        ),
        models.Client(
            firstName="alice",
            lastName="humfrey",
            emailAddress="alice.humphrey@example.com",
            preBecycleSurveyCompleted=False,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=False
        ),
        models.Client(
            firstName="debby",
            lastName="smith",
            emailAddress="debby.smith@exmaple.com",
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
        ),
        models.Client(
            firstName="notprovided",
            lastName="notprovided",
            emailAddress="sdjvhbsjvbwsjhdbv@notprovided.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=True
        ),
        models.Client(
            firstName="ab",
            lastName="cd",
            emailAddress="bgfdnggdbfdb@notprovided.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=True
        ),
        models.Client(
            firstName="ab",
            lastName="ef",
            emailAddress="dfnfdbdbfdbffggfr@notprovided.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=True
        ),
        models.Client(
            firstName="notprovided",
            lastName="notprovided",
            emailAddress="ewvrebsbsbrbsbsf@notprovided.com",
            preBecycleSurveyCompleted=True,
            periBecycleSurveyCompleted=True,
            postBecycleSurveyCompleted=True
        ),
    ]

    db.add_all(clients)
    db.commit()

    return clients


def add_detected_potential_client_duplicates(db: Session, clients: list[models.Client]) -> list[models.DetectedPotentialClientDuplicates]:
    client_duplicates = [
        models.DetectedPotentialClientDuplicates(  # definitely a duplicate but accidentally marked to ignore
            client1Id=clients[0].id,
            client2Id=clients[2].id,
            similarityScore=5,
            ignore=True
        ),
        models.DetectedPotentialClientDuplicates(  # not a duplicate and already marked to ignore
            client1Id=clients[3].id,
            client2Id=clients[1].id,
            similarityScore=2,
            ignore=True,
        ),
        models.DetectedPotentialClientDuplicates(  # definitely a duplicate
            client1Id=clients[4].id,
            client2Id=clients[1].id,
            similarityScore=5,
            ignore=False,
        ),
        models.DetectedPotentialClientDuplicates(  # not a duplicate
            client1Id=clients[4].id,
            client2Id=clients[3].id,
            similarityScore=2,
            ignore=False
        )
    ]

    db.add_all(client_duplicates)
    db.commit()

    return client_duplicates


def add_client_logins(db: Session, clients: list[models.Client]) -> list[models.ClientLogin]:
    client_logins = [
        models.ClientLogin(
            clientId=clients[1].id
        ),
        models.ClientLogin(
            clientId=clients[3].id
        )
    ]

    db.add_all(client_logins)
    db.commit()

    return client_logins


def add_client_logins_expired(db: Session, clients: list[models.Client]) -> list[models.ClientLogin]:
    client_logins_expired = [
        models.ClientLogin(
            clientId=clients[1].id,
            expirationDateTime=datetime.datetime.utcnow() - relativedelta(minutes=10)
        ),
        models.ClientLogin(
            clientId=clients[3].id,
            expirationDateTime=datetime.datetime.utcnow() - relativedelta(minutes=200)
        )
    ]

    db.add_all(client_logins_expired)
    db.commit()

    return client_logins_expired


def add_clients_temp(db: Session) -> list[models.ClientTemp]:
    clients_temp = [
        models.ClientTemp(
            firstName="echo",
            lastName="foxtrot",
            emailAddress="echo.foxtrot@example.com"
        ),
        models.ClientTemp(
            firstName="golf",
            lastName="hotel",
            emailAddress="golf.hotel@example.com",
            expirationDateTime=datetime.datetime.utcnow() - relativedelta(minutes=30)
        )
    ]

    db.add_all(clients_temp)
    db.commit()

    return clients_temp


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

def add_bikes_for_all_colours(db: Session) -> list[models.Bike]:
    bikes = []
    with open("data/all_colours.txt", "r") as f:
        for line in f:
            bikes.append(models.Bike(make="NOTPROVIDED", model="NOTPROVIDED", colour=line.strip(), decals=None, serialNumber="NOTPROVIDED"))

    db.add_all(bikes)
    db.commit()

    return bikes


def add_bikes_with_duplicates(db: Session) -> list[models.Bike]:
    bikes = [
        models.Bike(make="apollo", model="skidmarks", colour="brown", decals=None, serialNumber="abcd1234"),
        models.Bike(make="apollo", model="excelle", colour="black", decals=None, serialNumber="abcd1256"),
        models.Bike(make="apolo", model="skidmark", colour="brown", decals=None, serialNumber="bcd1234"),
        models.Bike(make="raleigh", model="chloe", colour="pink", decals=None, serialNumber="efgh5678"),
        models.Bike(make="raleigh", model="enigma", colour="blue and grey", decals=None, serialNumber="mnop3456"),
        models.Bike(make="raleigh", model="enigma", colour="black and grey", decals=None, serialNumber="qrst7890"),
        models.Bike(make="apollo", model="excelle", colour="green", decals=None, serialNumber="ijkl9012"),
        models.Bike(make="notprovided", model="notprovided", colour="notprovided", decals=None, serialNumber="notprovided"),
        models.Bike(make="notprovided", model="notprovided", colour="notprovided", decals=None,
                    serialNumber="notprovided"),
        models.Bike(make="ab", model="cd", colour="d", decals=None,
                    serialNumber="notprovided"),
        models.Bike(make="ralegh", model="engma", colour="black and grey", decals=None, serialNumber="qrst7890"),
    ]

    db.add_all(bikes)
    db.commit()

    return bikes


def add_detected_potential_bike_duplicates(db: Session, bikes: list[models.Bike]) -> list[models.DetectedPotentialBikeDuplicates]:
    bike_duplicates = [
        models.DetectedPotentialBikeDuplicates(  # definitely a duplicate
            bike1Id=bikes[0].id,
            bike2Id=bikes[2].id,
            similarityScore=5,
            ignore=False
        ),
        models.DetectedPotentialBikeDuplicates(  # not a duplicate
            bike1Id=bikes[1].id,
            bike2Id=bikes[6].id,
            similarityScore=4,
            ignore=False,
        ),
        models.DetectedPotentialBikeDuplicates(  # not a duplicate, marked to ignore
            bike1Id=bikes[5].id,
            bike2Id=bikes[4].id,
            similarityScore=7,
            ignore=True
        ),
        models.DetectedPotentialBikeDuplicates(  # not a duplicate, marked to ignore
            bike1Id=bikes[4].id,
            bike2Id=bikes[10].id,
            similarityScore=5,
            ignore=True
        ),
        models.DetectedPotentialBikeDuplicates(  # definitely a duplicate, marked to ignore
            bike1Id=bikes[10].id,
            bike2Id=bikes[5].id,
            similarityScore=8,
            ignore=True
        ),
    ]

    db.add_all(bike_duplicates)
    db.commit()

    return bike_duplicates


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
            treasurer=True,
            softDeleted=False),
        models.User(
            username="BANK",
            password=bcrypt.hashpw("bank1234", bcrypt.gensalt()),
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
            startDate=five_quarter_ago,
            endDate=three_quarter_ago,
            returnedDate=three_quarter_ago - relativedelta(months=1),
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
            startDate=six_quarter_ago - relativedelta(months=2),
            endDate=four_quarter_ago - relativedelta(months=2),
            returnedDate=six_quarter_ago,
            depositAmountCollected=40,
            depositAmountReturned=40,
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
            startDate=two_quarter_ago - relativedelta(months=1),
            endDate=today - relativedelta(months=1),
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
            startDate=one_quarter_ago,
            endDate=today + relativedelta(months=3),
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
            startDate=three_quarter_ago - relativedelta(months=1),
            endDate=one_quarter_ago - relativedelta(months=1),
            returnedDate=today - relativedelta(months=2),
            depositAmountCollected=40,
            depositAmountReturned=20,
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
            startDate=five_quarter_ago - relativedelta(months=1),
            endDate=three_quarter_ago - relativedelta(months=1),
            returnedDate=one_quarter_ago - relativedelta(months=2),
            depositAmountCollected=40,
            depositAmountReturned=10,
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
            startDate=two_quarter_ago - relativedelta(months=1),
            endDate=today - relativedelta(months=1),
            returnedDate=today - relativedelta(months=2),
            depositAmountCollected=40,
            depositAmountReturned=30,
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



def add_contracts_test_reminders(db: Session, users: list[models.User], clients: list[models.Client], bikes: list[models.Bike], contract_types: list[models.ContractType]) -> list[models.Contract]:
    past_date_2 = datetime.datetime.utcnow().date() - relativedelta(weeks=2)
    past_date_1 = datetime.datetime.utcnow().date() - relativedelta(weeks=1)
    future_date_1 = datetime.datetime.utcnow().date() + relativedelta(weeks=1)
    future_date_2 = datetime.datetime.utcnow().date() + relativedelta(weeks=2)
    future_date_3 = datetime.datetime.utcnow().date() + relativedelta(weeks=3)

    contracts = [
        models.Contract(  # no reminder, already past
            clientId=clients[0].id,
            bikeId=bikes[0].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=past_date_2,
            endDate=past_date_1,
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="fair",
            contractType=contract_types[0].id,
            notes="returned on time",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(  # no reminder, already returned
            clientId=clients[1].id,
            bikeId=bikes[1].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[0].id,
            returnAcceptingUserId=users[0].id,
            depositReturningUserId=users[0].id,
            startDate=past_date_2,
            endDate=future_date_1,
            returnedDate=past_date_1,
            depositAmountCollected=40,
            depositAmountReturned=40,
            conditionOfBike="fair",
            contractType=contract_types[1].id,
            notes="returned very early",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(  # no reminder, already sent
            clientId=clients[2].id,
            bikeId=bikes[2].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=past_date_2,
            endDate=future_date_1,
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="good",
            contractType=contract_types[0].id,
            notes="this should be expired",
            detailsSent=True,
            expiryReminderSent=True,
            returnDetailsSent=False
        ), models.Contract(  # reminder
            clientId=clients[3].id,
            bikeId=bikes[3].id,
            workingUserId=users[0].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=past_date_2,
            endDate=future_date_1,
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="fair",
            contractType=contract_types[2].id,
            notes="this one is open",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ),
        models.Contract(  # reminder
            clientId=clients[2].id,
            bikeId=bikes[5].id,
            workingUserId=users[2].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=past_date_2,
            endDate=future_date_2,
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
            conditionOfBike="fair",
            contractType=contract_types[1].id,
            notes="returned very late",
            detailsSent=True,
            expiryReminderSent=False,
            returnDetailsSent=False
        ), models.Contract(  # no reminder
            clientId=clients[4].id,
            bikeId=bikes[6].id,
            workingUserId=users[2].id,
            checkingUserId=users[1].id,
            depositCollectingUserId=users[2].id,
            returnAcceptingUserId=None,
            depositReturningUserId=None,
            startDate=past_date_2,
            endDate=future_date_3,
            returnedDate=None,
            depositAmountCollected=40,
            depositAmountReturned=None,
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


def add_paper_contracts(db: Session, contracts: list[models.Contract]) -> list[models.PaperContract]:
    paper_contracts = [
        models.PaperContract(
            id="123456abcdef789012ghijkl",
            contractId=contracts[0].id,
        ),
        models.PaperContract(
            id="lkjihg210987fedcba654321",
            contractId=contracts[1].id,
        ),
        models.PaperContract(
            id="123456fedcba789012lkjihg",
            contractId=contracts[2].id,
        ),
    ]

    db.add_all(paper_contracts)
    db.commit()

    return paper_contracts


def add_appointment_types(db: Session) -> list[models.AppointmentType]:
    appointment_types = [
        models.AppointmentType(
            id="rent",
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
        ),
        models.AppointmentType(
            id="srep",
            active=False,
            title="Small Repair",
            description="You know what this is",
            duration=30
        )
    ]

    db.add_all(appointment_types)
    db.commit()

    return appointment_types


def add_appointments(db: Session, clients: list[models.Client], appointment_types: list[models.AppointmentType], appointment_general_settings: models.AppointmentGeneralSettings) -> list[models.Appointment]:
    past_date_1 = datetime.datetime.utcnow().date() - relativedelta(days=1)
    while past_date_1.weekday() not in appointment_general_settings.openingDays:
        past_date_1 -= relativedelta(days=1)

    past_date_2 = past_date_1 - relativedelta(days=1)
    while past_date_2.weekday() not in appointment_general_settings.openingDays:
        past_date_2 -= relativedelta(days=1)

    future_date_1 = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while future_date_1.weekday() not in appointment_general_settings.openingDays:
        future_date_1 += relativedelta(days=1)

    future_date_2 = future_date_1 + relativedelta(days=1)
    while future_date_2.weekday() not in appointment_general_settings.openingDays:
        future_date_2 += relativedelta(days=1)

    appointments = [
        models.Appointment(
            clientId=clients[0].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[1].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[2].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[2].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=19, minute=15)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[3].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(past_date_2, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(past_date_2, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[3].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=True,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[3].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=17, minute=15)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[4].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[4].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=17, minute=45)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=19, minute=45)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(
            clientId=clients[4].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=18, minute=45)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=19, minute=45)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=True
        ),
    ]

    db.add_all(appointments)
    db.commit()

    return appointments


def add_appointments_test_reminders(db: Session, clients: list[models.Client], appointment_types: list[models.AppointmentType], appointment_general_settings: models.AppointmentGeneralSettings) -> list[models.Appointment]:
    past_date_1 = datetime.datetime.utcnow().date() - relativedelta(days=2)
    future_date_1 = datetime.datetime.utcnow().date() + relativedelta(days=2)
    future_date_2 = datetime.datetime.utcnow().date() + relativedelta(days=4)

    appointments = [
        models.Appointment(  # no reminder
            clientId=clients[0].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=False
        ),
        models.Appointment(  # no reminder
            clientId=clients[1].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(past_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(  # no reminder
            clientId=clients[2].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(  # no reminder
            clientId=clients[2].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=19, minute=15)),
            notes=None,
            confirmed=False,
            cancelled=False,
            reminderSent=False
        ),
        models.Appointment(  # no reminder
            clientId=clients[3].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=True,
            reminderSent=False
        ),
        models.Appointment(  # reminder
            clientId=clients[3].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=False
        ),
        models.Appointment(  # no reminder
            clientId=clients[3].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_1, datetime.time(hour=17, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=True,
            reminderSent=True
        ),
        models.Appointment(  # no reminder
            clientId=clients[4].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=16, minute=15)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=18, minute=15)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=False
        ),
        models.Appointment(  # no reminder
            clientId=clients[4].id,
            typeId=appointment_types[0].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=17, minute=45)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=19, minute=45)),
            notes=None,
            confirmed=True,
            cancelled=False,
            reminderSent=True
        ),
        models.Appointment(  # no reminder
            clientId=clients[4].id,
            typeId=appointment_types[1].id,
            startDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=18, minute=45)),
            endDateTime=datetime.datetime.combine(future_date_2, datetime.time(hour=19, minute=45)),
            notes=None,
            confirmed=True,
            cancelled=True,
            reminderSent=False
        ),
    ]

    db.add_all(appointments)
    db.commit()

    return appointments


def add_appointment_settings(db: Session) -> models.AppointmentGeneralSettings:
    appointment_settings = models.AppointmentGeneralSettings(
        openingDays=[0, 2],
        minBookAhead=2,
        maxBookAhead=21,
        slotDuration=15,
        gradualAvailability=True
    )

    db.add(appointment_settings)
    db.commit()

    return appointment_settings


def add_appointment_concurrency_limits(db: Session) -> list[models.AppointmentConcurrencyLimit]:
    appointment_concurrency_limits = [
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=0, minute=0),
            maxConcurrent=0,
            weekDay=0
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=16, minute=15),
            maxConcurrent=2,
            weekDay=0
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=17, minute=30),
            maxConcurrent=4,
            weekDay=0
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=19, minute=45),
            maxConcurrent=0,
            weekDay=0
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=0, minute=0),
            maxConcurrent=0,
            weekDay=2
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=16, minute=15),
            maxConcurrent=3,
            weekDay=2
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=17, minute=30),
            maxConcurrent=6,
            weekDay=2
        ),
        models.AppointmentConcurrencyLimit(
            afterTime=datetime.time(hour=19, minute=45),
            maxConcurrent=0,
            weekDay=2
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


def add_closed_days(db: Session, appointment_general_settings: models.AppointmentGeneralSettings) -> list[models.ClosedDay]:
    future_date_1 = datetime.datetime.utcnow().date() + relativedelta(days=appointment_general_settings.minBookAhead)
    while future_date_1.weekday() not in appointment_general_settings.openingDays:
        future_date_1 += relativedelta(days=1)

    future_date_2 = future_date_1 + relativedelta(days=1)
    while future_date_2.weekday() not in appointment_general_settings.openingDays:
        future_date_2 += relativedelta(days=1)

    future_date_3 = future_date_2 + relativedelta(days=1)
    while future_date_3.weekday() not in appointment_general_settings.openingDays:
        future_date_3 += relativedelta(days=1)

    closed_days = [
        models.ClosedDay(
            date=future_date_3,
            note="Workshop Day"
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
        ),
        models.DepositExchange(
            amount=40,
            fromUserId=users[6].id,
            toUserId=users[2].id,
            date=(datetime.datetime.utcnow().date() - relativedelta(months=3))
        )
    ]

    db.add_all(deposit_exchanges)
    db.commit()

    return deposit_exchanges


def add_expense_types(db: Session) -> list[models.ExpenseType]:
    expense_types = [
        models.ExpenseType(
            id="consumables",
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


def add_expense_tags(db: Session) -> list[models.ExpenseTag]:
    expense_tags = [
        models.ExpenseTag(
            id="workshop",
            description="Regular workshop expenses"
        ),
        models.ExpenseTag(
            id="test",
            description="Just testing"
        ),
    ]

    db.add_all(expense_tags)
    db.commit()

    return expense_tags


def add_expense_receipts(db: Session) -> list[models.ExpenseReceipt]:
    expense_receipts = []

    current_directory = os.path.dirname(os.path.abspath(__file__))
    photos_directory = os.path.join(current_directory, "tests", "photos")
    for i in range(3):
        photo_path = os.path.join(photos_directory, f"receipt{i}.jpg")
        with open(photo_path, "rb") as photo:
            expense_receipts.append(
                models.ExpenseReceipt(
                    content=photo.read()
                )
            )

    for i in range(3, 5):
        pdf_path = os.path.join(photos_directory, f"receipt{i}.pdf")
        with open(pdf_path, "rb") as pdf:
            expense_receipts.append(
                models.ExpenseReceipt(
                    content=pdf.read()
                )
            )

    db.add_all(expense_receipts)
    db.commit()

    return expense_receipts


def add_expenses(db: Session, expense_receipts: list[models.ExpenseReceipt], users: list[models.User], expense_types: list[models.ExpenseType], expense_tags: list[models.ExpenseTag]) -> list[models.Expense]:
    expenses = [
        models.Expense(
            expenseUserId=users[2].id,
            treasurerUserId=users[0].id,
            expenseDate=datetime.datetime.utcnow().date() - relativedelta(months=15),
            transferDate=datetime.datetime.utcnow().date() - relativedelta(months=9),
            amount=-40,
            type=expense_types[1].id,
            notes="brake pads",
            receiptFileId=expense_receipts[0].id,
            receiptContentType="image/jpeg",
            tagId=expense_tags[0].id,
        ),
        models.Expense(
            expenseUserId=users[1].id,
            treasurerUserId=users[0].id,
            expenseDate=datetime.datetime.utcnow().date() - relativedelta(months=11),
            transferDate=datetime.datetime.utcnow().date() - relativedelta(months=9),
            amount=-30,
            type=expense_types[0].id,
            notes="chain oil",
            receiptFileId=expense_receipts[1].id,
            receiptContentType="image/jpeg",
            tagId=expense_tags[1].id,
        ),
        models.Expense(
            expenseUserId=users[0].id,
            treasurerUserId=users[0].id,
            expenseDate=datetime.datetime.utcnow().date() - relativedelta(months=7),
            transferDate=datetime.datetime.utcnow().date() - relativedelta(months=4),
            amount=+100,
            type=expense_types[2].id,
            notes="cash from safe",
            receiptFileId=expense_receipts[2].id,
            receiptContentType="image/jpeg",
            tagId=expense_tags[0].id,
        ),
        models.Expense(
            expenseUserId=users[0].id,
            treasurerUserId=None,
            expenseDate=datetime.datetime.utcnow().date() - relativedelta(months=2),
            transferDate=None,
            amount=-80,
            type=expense_types[1].id,
            notes="chains",
            receiptFileId=expense_receipts[3].id,
            receiptContentType="application/pdf",
            tagId=expense_tags[1].id,
        ),
        models.Expense(
            expenseUserId=users[2].id,
            treasurerUserId=None,
            expenseDate=datetime.datetime.utcnow().date() - relativedelta(months=1),
            transferDate=None,
            amount=-40,
            type=expense_types[0].id,
            notes="gt-85",
            receiptFileId=expense_receipts[4].id,
            receiptContentType="application/pdf",
            tagId=expense_tags[0].id,
        ),
    ]

    db.add_all(expenses)
    db.commit()

    return expenses


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


def add_road_segments(db: Session) -> list[models.RoadSegment]:
    from_latitudes = [57.160228, 57.152243, 57.141279, 57.192152, 57.192543, 57.192543, 57.186599, 57.185582, 57.194733, 57.19442, 57.174394, 57.173533, 57.168055, 57.166177]
    from_longitudes = [-2.196017, -2.197316, -2.199048, -2.166281, -2.145495, -2.120667, -2.122976, -2.123265, -2.139143, -2.137267, -2.234991, -2.236723, -2.205544, -2.203667]
    to_latitudes = [57.169307, 57.160228, 57.152243, 57.192543, 57.192543, 57.192309, 57.188085, 57.186599, 57.19442, 57.194264, 57.175255, 57.174394, 57.167116, 57.167116]
    to_longitudes = [-2.195007, -2.196017, -2.197316, -2.145495, -2.120667, -2.086456, -2.122976, -2.122976, -2.137267, -2.135823, -2.233548, -2.234991, -2.204534, -2.204534]
    road_classifications = ["A Road", "A Road", "A Road", "A Road", "A Road", "A Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road"]
    road_functions = ["A Road", "A Road", "A Road", "A Road", "A Road", "A Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road", "B Road"]
    form_of_ways = ["Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Dual Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway", "Single Carriageway"]
    names = ["Big Street One", "Big Street One", "Big Street One", "Big Street Two", "Big Street Two", "Big Street Two", "Small Street One", "Small Street One", "Small Street Two", "Small Street Two", "Small Street Three", "Small Street Three", "Small Street Four", "Small Street Four"]
    lengths = [1011, 891, 1224, 1253, 1496, 2061, 165, 114, 118, 89, 129, 142, 121, 117]

    road_segments = [
        models.RoadSegment(
            fromLatitude=from_latitudes[i],
            fromLongitude=from_longitudes[i],
            toLatitude=to_latitudes[i],
            toLongitude=to_longitudes[i],
            roadClassification=road_classifications[i],
            roadFunction=road_functions[i],
            formOfWay=form_of_ways[i],
            name=names[i],
            length=lengths[i],
        ) for i in range(14)
    ]

    db.add_all(road_segments)
    db.commit()

    return road_segments


def add_road_segment_report_types(db: Session) -> list[models.RoadSegmentReportType]:
    road_segment_report_types = [
        models.RoadSegmentReportType(
            id="path",
            title="Cycle Path",
            description="A Segregated Cycle Path",
            scoreModifier=+4,
        ),
        models.RoadSegmentReportType(
            id="cycle",
            title="Cycle Lane",
            description="A Cycle Lane",
            scoreModifier=+2,
        ),
        models.RoadSegmentReportType(
            id="potho",
            title="Pothole",
            description="A Pothole",
            scoreModifier=-2,
        ),
        models.RoadSegmentReportType(
            id="poths",
            title="Potholes",
            description="Many Potholes",
            scoreModifier=-2,
        )
    ]

    db.add_all(road_segment_report_types)
    db.commit()

    return road_segment_report_types


def add_road_segment_reports(db: Session, road_segment_report_types: list[models.RoadSegmentReportType], road_segments: list[models.RoadSegment]) -> list[models.RoadSegmentReport]:
    road_segment_reports = [
        models.RoadSegmentReport(
            roadSegmentId=road_segments[1].id,
            typeId=road_segment_report_types[0].id
        ),
        models.RoadSegmentReport(
            roadSegmentId=road_segments[4].id,
            typeId=road_segment_report_types[1].id
        ),
        models.RoadSegmentReport(
            roadSegmentId=road_segments[6].id,
            typeId=road_segment_report_types[2].id
        ),
        models.RoadSegmentReport(
            roadSegmentId=road_segments[8].id,
            typeId=road_segment_report_types[3].id
        ),
        models.RoadSegmentReport(
            roadSegmentId=road_segments[10].id,
            typeId=road_segment_report_types[0].id
        ),
        models.RoadSegmentReport(
            roadSegmentId=road_segments[12].id,
            typeId=road_segment_report_types[1].id
        ),
    ]

    db.add_all(road_segment_reports)
    db.commit()

    return road_segment_reports


def add_permissions(db: Session) -> list[models.Permission]:
    from main import app
    # import crud
    # crud.ensure_all_permissions_exist(db=db, routes=[route for route in app.routes if isinstance(route, APIRoute)])
    # crud.prune_permissions_tree(db=db)

    return [_ for _ in db.scalars(
        select(models.Permission)
    )]


def add_admin_group(db: Session, permissions: list[models.Permission], users: list[models.User]) -> list[models.Group]:
    groups = [
        models.Group(
            name="admin",
        )
    ]

    db.add_all(groups)
    db.commit()

    for group in groups:
        for permission in permissions:
            if group.name == "admin" and permission.route == "/":
                group.permissions.append(permission)
                db.commit()

        for user in users:
            if user.username == "elaine":
                user.groups.append(group)
                db.commit()

    return groups


if __name__ == "__main__":
    from app.database.db import Base, engine, SessionLocal

    Base.metadata.create_all(bind=engine)
    demo_db = SessionLocal()

    delete_all(db=demo_db)

    demo_users = add_users(db=demo_db)
    #demo_bikes = add_bikes(db=demo_db)
    demo_bikes = add_bikes_for_all_colours(db=demo_db)
    demo_clients = add_clients(db=demo_db)
    demo_user_photos = add_user_photos(db=demo_db, users=demo_users)
    demo_user_presentation_cards = add_user_presentation_cards(db=demo_db, users=demo_users, user_photos=demo_user_photos)
    demo_contract_types = add_contract_types(db=demo_db)
    demo_contracts = add_contracts(db=demo_db, users=demo_users, clients=demo_clients, bikes=demo_bikes, contract_types=demo_contract_types)
    demo_appointment_types = add_appointment_types(db=demo_db)
    demo_appointment_general_settings = add_appointment_settings(db=demo_db)
    demo_appointment_concurrency_limits = add_appointment_concurrency_limits(db=demo_db)
    demo_appointments = add_appointments(db=demo_db, appointment_types=demo_appointment_types, clients=demo_clients, appointment_general_settings=demo_appointment_general_settings)
    demo_address = add_address(db=demo_db)
    demo_closed_days = add_closed_days(db=demo_db, appointment_general_settings=demo_appointment_general_settings)
    demo_deposit_exchanges = add_deposit_exchanges(db=demo_db, users=demo_users)
    demo_expense_types = add_expense_types(db=demo_db)
    demo_expense_tags = add_expense_tags(db=demo_db)
    demo_expense_receipts = add_expense_receipts(db=demo_db)
    demo_expenses = add_expenses(db=demo_db, expense_receipts=demo_expense_receipts, users=demo_users, expense_types=demo_expense_types, expense_tags=demo_expense_tags)
    demo_paper_contracts = add_paper_contracts(db=demo_db, contracts=demo_contracts)
    demo_road_segments = add_road_segments(db=demo_db)
    demo_road_segment_report_types = add_road_segment_report_types(db=demo_db)
    demo_road_segment_reports = add_road_segment_reports(db=demo_db, road_segments=demo_road_segments, road_segment_report_types=demo_road_segment_report_types)
    demo_permissions = add_permissions(db=demo_db)
    demo_groups = add_admin_group(db=demo_db, permissions=demo_permissions, users=demo_users)