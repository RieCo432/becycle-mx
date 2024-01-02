import datetime

from dateutil.relativedelta import relativedelta

import app.models as models
from app.database.db import SessionLocal
import bcrypt


db = SessionLocal()

db.query(models.Contract).delete()
db.query(models.Bike).delete()
db.query(models.DepositExchange).delete()
db.query(models.Appointment).delete()
db.query(models.AppointmentType).delete()
db.query(models.Client).delete()
db.query(models.ClosedDay).delete()
db.query(models.User).delete()

demo_clients = [
    models.Client(firstName="Alice", lastName="Humphrey", emailAddress="alice.humphrey@example.com"),
    models.Client(firstName="Bob", lastName="Frank", emailAddress="bob.frank@example.com"),
    models.Client(firstName="Charlie", lastName="Maurice", email="charlie.maurice@example.com"),
    models.Client(firstName="Daurice", lastName="Smith", email="daurice.smith@exmaple.com")
]

db.add_all(demo_clients)
db.commit()

demo_bikes = [
    models.Bike(make="Apollo", model="Skidmarks", colour="Brown", decals=None, serialNumber="abcd1234"),
    models.Bike(make="Raleigh", model="Chloe", colour="Pink", decals=None, serialNumber="efgh5678"),
    models.Bike(make="ElephantBike", model="Heavy AF", colour="Blue", decals=None, serialNumber="ijkl9012")
]

db.add_all(demo_bikes)
db.commit()

demo_users = [
    models.User(
        username="elaine",
        password=bcrypt.hashpw("password", bcrypt.gensalt()),
        pin=bcrypt.hashpw("1234", bcrypt.gensalt()),
        admin=True,
        depositBearer=True,
        rentalChecker=True,
        appointmentManager=True,
        treasurer=True,
        softDeleted=False),

    models.User(
        username="freddy",
        password=bcrypt.hashpw("freddy123", bcrypt.gensalt()),
        pin=bcrypt.hashpw("0000", bcrypt.gensalt()),
        admin=False,
        depositBearer=False,
        rentalChecker=True,
        appointmentManager=True,
        treasurer=False,
        softDeleted=False),

    models.User(
        username="george",
        password=bcrypt.hashpw("test1234", bcrypt.gensalt()),
        pin=bcrypt.hashpw("1111", bcrypt.gensalt()),
        admin=False,
        depositBearer=True,
        rentalChecker=False,
        appointmentManager=False,
        treasurer=False,
        softDeleted=False),

    models.User(
        username="honey",
        password=bcrypt.hashpw("honey123", bcrypt.gensalt()),
        pin=bcrypt.hashpw("9999", bcrypt.gensalt()),
        admin=False,
        depositBearer=False,
        rentalChecker=False,
        appointmentManager=False,
        treasurer=False,
        softDeleted=True),
]

db.add_all(demo_users)
db.commit()

demo_contracts = [models.Contract(
        clientId=demo_clients[0].id,
        bikeId=demo_bikes[0].id,
        workingUserId=demo_users[0].id,
        checkingUserId=demo_users[1].id,
        depositCollectingUserId=demo_users[0].id,
        returnAcceptingUserId=None,
        depositReturningUserId=None,
        startDate=(datetime.datetime.utcnow() - relativedelta(month=3)).date(),
        endDate=(datetime.datetime.utcnow() + relativedelta(month=3)).date(),
        returnedDate=None,
        depositAmountCollected=40,
        depositAmountReturned=None,
        conditionOfBike="okay",
        contractType="standard",
        notes="loose saddle",
        detailsSent=True,
        expiryReminderSent=False,
        returnDetailsSent=False
    ),models.Contract(
        clientId=demo_clients[1].id,
        bikeId=demo_bikes[1].id,
        workingUserId=demo_users[3].id,
        checkingUserId=demo_users[0].id,
        depositCollectingUserId=demo_users[2].id,
        returnAcceptingUserId=None,
        depositReturningUserId=None,
        startDate=(datetime.datetime.utcnow() - relativedelta(month=2)).date(),
        endDate=(datetime.datetime.utcnow() + relativedelta(month=4)).date(),
        returnedDate=None,
        depositAmountCollected=40,
        depositAmountReturned=None,
        conditionOfBike="good",
        contractType="standard",
        notes=None,
        detailsSent=True,
        expiryReminderSent=False,
        returnDetailsSent=False
    ),
    models.Contract(
        clientId=demo_clients[2].id,
        bikeId=demo_bikes[2].id,
        workingUserId=demo_users[2].id,
        checkingUserId=demo_users[0].id,
        depositCollectingUserId=demo_users[2].id,
        returnAcceptingUserId=demo_users[1].id,
        depositReturningUserId=demo_users[2].id,
        startDate=(datetime.datetime.utcnow() - relativedelta(month=5)).date(),
        endDate=(datetime.datetime.utcnow() + relativedelta(month=1)).date(),
        returnedDate=(datetime.datetime.utcnow() - relativedelta(month=1)).date(),
        depositAmountCollected=10,
        depositAmountReturned=10,
        conditionOfBike="okay",
        contractType="refugee",
        notes=None,
        detailsSent=True,
        expiryReminderSent=False,
        returnDetailsSent=False),
]

db.add_all(demo_contracts)
db.commit()


demo_appointment_types = [
    models.AppointmentType(
        active=True,
        title="Lending",
        description="You know what this is",
        duration=120
    ),
    models.AppointmentType(
        active=True,
        title="Medium Repair",
        description="You know what this is",
        duration=60
    )
]

db.add_all(demo_appointment_types)
db.commit()


demo_appointments = [
    models.Appointment(
        clientId=demo_clients[1],
        typeId=demo_appointment_types[0],
        startDateTime=datetime.datetime.combine((datetime.datetime.utcnow() - relativedelta(month=2)).date(), datetime.time(hour=16, minute=15)),
        endDateTime=datetime.datetime.combine((datetime.datetime.utcnow() - relativedelta(month=2)).date(), datetime.time(hour=18, minute=15)),
        notes=None,
        confirmed=True,
        cancelled=False,
        reminderSent=True
    ),
    models.Appointment(
        clientId=demo_clients[3],
        typeId=demo_appointment_types[1],
        startDateTime=datetime.datetime.combine((datetime.datetime.utcnow() + relativedelta(days=2)).date(), datetime.time(hour=16, minute=15)),
        endDateTime=datetime.datetime.combine((datetime.datetime.utcnow() + relativedelta(days=2)).date(), datetime.time(hour=18, minute=15)),
        notes=None,
        confirmed=True,
        cancelled=False,
        reminderSent=True
    )
]

db.add_all(demo_appointments)
db.commit()
