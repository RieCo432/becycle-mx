from fastapi import Depends

from mongodb import get_contracts, deref, get_users
import app.models as models
from app.database.db import SessionLocal


db = SessionLocal()


db.query(models.Contract).delete()
db.query(models.Bike).delete()
db.query(models.DepositExchange).delete()


db.query(models.User).delete()

for mongo_user in get_users():
    mongo_username = mongo_user["username"]
    mongo_password = mongo_user["password"]
    mongo_pin = mongo_user["pin"] if "pin" in mongo_user else None
    mongo_admin = mongo_user["admin"]
    mongo_appointment_manager = mongo_user["appointmentManager"]
    mongo_deposit_bearer = mongo_user["depositBearer"]
    mongo_treasurer = mongo_user["treasurer"]
    mongo_rental_checker = mongo_user["rentalChecker"]
    mongo_soft_deleted = mongo_user["softDeleted"]

    postres_user = models.User(
        username=mongo_username,
        password=mongo_password,
        pin=mongo_pin,
        admin=mongo_admin,
        depositBearer=mongo_deposit_bearer,
        rentalChecker=mongo_rental_checker,
        appointmentManager=mongo_appointment_manager,
        treasurer=mongo_treasurer,
        softDeleted=mongo_soft_deleted
    )

    db.add(postres_user)

db.commit()


for mongo_contract in get_contracts():
    mongo_bike = deref(mongo_contract["bike"])
    mongo_person = deref(mongo_contract["person"])
