from fastapi import Depends

from mongodb import *
import app.models as models
from app.database.db import SessionLocal
from app.crud.users import get_user
import json


db = SessionLocal()


db.query(models.Contract).delete()
db.query(models.Bike).delete()
db.query(models.DepositExchange).delete()
db.query(models.Appointment).delete()
db.query(models.AppointmentType).delete()
db.query(models.Client).delete()
db.query(models.ClosedDay).delete()
db.query(models.User).delete()

user_map = {}

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

    user_map[mongo_username] = postres_user.id

bike_map = {}

for mongo_bike in get_bikes():
    mongo_make = mongo_bike.get("make", None)
    mongo_model = mongo_bike.get("model", None)
    mongo_colour = mongo_bike.get("colour", None)
    mongo_decals = mongo_bike.get("decals", None)
    mongo_serialnumber = mongo_bike.get("serialNumber", None)

    mongo_decals = None if mongo_decals.lower() == "notprovided" or mongo_decals.lower() == "none" else mongo_decals
    mongo_serialnumber = "n/a" if mongo_serialnumber is None or mongo_serialnumber.lower() == "notprovided" else mongo_serialnumber

    postgres_bike = models.Bike(
        make=mongo_make,
        model=mongo_model,
        colour=mongo_colour,
        decals=mongo_decals,
        serialNumber=mongo_serialnumber,
    )

    db.add(postgres_bike)
    db.commit()

    bike_map[mongo_bike["_id"]] = postgres_bike.id


client_map = {}
client_map_email = {}

for mongo_person in get_persons():
    mongo_first_name = mongo_person["firstName"]
    mongo_last_name = mongo_person["lastName"]
    mongo_email_address = mongo_person["emailAddress"]

    postgres_client = models.Client(
        firstName=mongo_first_name,
        lastName=mongo_last_name,
        emailAddress=mongo_email_address
    )

    db.add(postgres_client)
    db.commit()

    client_map_email[mongo_person["emailAddress"]] = postgres_client.id
    client_map[mongo_person["_id"]] = postgres_client.id


for mongo_appointment_type in get_appointment_types():
    mongo_short = mongo_appointment_type["short"]
    mongo_active = mongo_appointment_type["active"]
    mongo_title = mongo_appointment_type["title"]
    mongo_description = mongo_appointment_type["description"]
    mongo_duration = mongo_appointment_type["duration"]

    postgres_appointment_type = models.AppointmentType(
        id=mongo_short,
        active=mongo_active,
        title=mongo_title,
        description=mongo_description,
        duration=mongo_duration
    )

    db.add(postgres_appointment_type)
    db.commit()


for mongo_appointment in get_appointments():
    mongo_additional_information = mongo_appointment["additionalInformation"]
    mongo_appointment_confirmation_email_sent = mongo_appointment["appointmentConfirmationEmailSent"]
    mongo_appointment_confirmed = mongo_appointment["appointmentConfirmed"]
    mongo_appointment_reminder_email_sent = mongo_appointment["appointmentReminderEmailSent"]
    mongo_cancelled = mongo_appointment["cancelled"]
    mongo_email_address = mongo_appointment["emailAddress"]
    mongo_email_verification_cutoff = mongo_appointment["emailVerificationCutoff"]
    mongo_email_verified = mongo_appointment["emailVerified"]
    mongo_end_datetime = mongo_appointment["endDateTime"]
    mongo_first_name = mongo_appointment["firstName"]
    mongo_last_name = mongo_appointment["lastName"]
    mongo_ref = mongo_appointment["ref"]
    mongo_start_datetime = mongo_appointment["startDateTime"]
    mongo_type = mongo_appointment["type"]

    postgres_client_id = client_map_email.get(mongo_email_address, None)
    if postgres_client_id is None:
        print("adding client: {}".format(mongo_email_address)) 
        postgres_client = models.Client(
            firstName=mongo_first_name,
            lastName=mongo_last_name,
            emailAddress=mongo_email_address
        )

        db.add(postgres_client)
        db.commit()

        postgres_client_id = postgres_client.id

    postgres_appointment = models.Appointment(
        clientId=postgres_client_id,
        typeId=mongo_type,
        startDateTime=mongo_start_datetime,
        endDateTime=mongo_end_datetime,
        notes=mongo_additional_information,
        confirmed=mongo_appointment_confirmed,
        cancelled=mongo_cancelled,
        reminderSent=mongo_appointment_reminder_email_sent
    )

    db.add(postgres_appointment)
    db.commit()

try:
    with open("loosely_typed_names_map.json", "r") as fin:
        loosely_typed_names_map = json.load(fin)
except FileNotFoundError:
    loosely_typed_names_map = {}


for mongo_contract in get_contracts():
    mongo_bike = deref(mongo_contract["bike"])
    mongo_checking_volunteer = mongo_contract["checkingVolunteer"]
    mongo_condition = mongo_contract["condition"]
    mongo_contract_sent_to_email = mongo_contract["contractSentToEmail"]
    mongo_contract_type = mongo_contract["contractType"]
    mongo_deposit_amount_paid = mongo_contract["depositAmountPaid"]
    mongo_deposit_amount_returned = mongo_contract["depositAmountReturned"]
    mongo_deposit_collected_by = mongo_contract["depositCollectedBy"]
    mongo_deposit_returned_by = mongo_contract["depositReturnedBy"]
    mongo_end_date = mongo_contract["endDate"]
    mongo_expiry_reminder_sent_to_email = mongo_contract["expiryReminderSentToEmail"]
    mongo_notes = mongo_contract["notes"]
    mongo_person = deref(mongo_contract["person"])
    mongo_returned_date = mongo_contract["returnedDate"]
    mongo_start_date = mongo_contract["startDate"]
    mongo_volunteer_received = mongo_contract["volunteerReceived"]
    mongo_working_volunteer = mongo_contract["workingVolunteer"]

    postgres_working_user = get_user(mongo_working_volunteer, db=db)
    if postgres_working_user is None and mongo_working_volunteer in loosely_typed_names_map:
        postgres_working_user = get_user(loosely_typed_names_map[mongo_working_volunteer], db=db)
    if postgres_working_user is None:
        manual_username = input("Enter username for '{}': ".format(mongo_working_volunteer))
        loosely_typed_names_map[mongo_working_volunteer] = manual_username
        postgres_working_user = get_user(manual_username, db=db)

    postgres_checking_user = get_user(mongo_checking_volunteer, db=db)
    if postgres_checking_user is None and mongo_checking_volunteer in loosely_typed_names_map:
        postgres_checking_user = get_user(loosely_typed_names_map[mongo_checking_volunteer], db=db)
    if postgres_checking_user is None:
        manual_username = input("Enter username for '{}': ".format(mongo_checking_volunteer))
        loosely_typed_names_map[mongo_checking_volunteer] = manual_username
        postgres_checking_user = get_user(manual_username, db=db)

    postgres_deposit_collecting_user = get_user(mongo_deposit_collected_by, db=db)
    if postgres_deposit_collecting_user is None and mongo_deposit_collected_by in loosely_typed_names_map:
            postgres_deposit_collecting_user = get_user(loosely_typed_names_map[mongo_deposit_collected_by], db=db)
    if postgres_deposit_collecting_user is None:
        manual_username = input("Enter username for '{}': ".format(mongo_deposit_collected_by))
        loosely_typed_names_map[mongo_deposit_collected_by] = manual_username
        postgres_deposit_collecting_user = get_user(manual_username, db=db)

    postgres_return_accepting_user = get_user(mongo_volunteer_received, db=db)
    if postgres_return_accepting_user is None and mongo_volunteer_received in loosely_typed_names_map:
        postgres_return_accepting_user = get_user(loosely_typed_names_map[mongo_volunteer_received], db=db)
    if postgres_return_accepting_user is None:
        manual_username = input("Enter username for '{}': ".format(mongo_volunteer_received))
        loosely_typed_names_map[mongo_volunteer_received] = manual_username
        postgres_return_accepting_user = get_user(manual_username, db=db)

    postgres_deposit_returning_user = get_user(mongo_deposit_returned_by, db=db)
    if postgres_deposit_returning_user is None and mongo_deposit_returned_by in loosely_typed_names_map:
        postgres_deposit_returning_user = get_user(loosely_typed_names_map[mongo_deposit_returned_by], db=db)
    if postgres_deposit_returning_user is None:
        manual_username = input("Enter username for '{}': ".format(mongo_deposit_returned_by))
        loosely_typed_names_map[mongo_deposit_returned_by] = manual_username
        postgres_deposit_returning_user = get_user(manual_username, db=db)

    postgres_bike_id = bike_map[mongo_bike["_id"]]
    postgres_client_id = client_map[mongo_person["_id"]]

    postgres_contract = models.Contract(
        clientId=postgres_client_id,
        bikeId=postgres_bike_id,
        workingUserId=postgres_working_user.id,
        checkingUserId=postgres_checking_user.id,
        depositCollectingUserId=postgres_deposit_collecting_user.id,
        returnAcceptingUserId=postgres_return_accepting_user.id,
        depositReturningUserId=postgres_deposit_returning_user.id,
        startDate=mongo_start_date,
        endDate=mongo_end_date,
        returnedDate=mongo_returned_date,
        depositAmountCollected=mongo_deposit_amount_paid,
        depositAmountReturned=mongo_deposit_amount_returned,
        conditionOfBike=mongo_condition,
        contractType=mongo_contract_type,
        notes=mongo_notes,
        detailsSent=mongo_contract_sent_to_email,
        expiryReminderSent=mongo_expiry_reminder_sent_to_email,
        returnDetailsSent=False
    )

    db.add(postgres_contract)
    db.commit()

with open("loosely_typed_names_map.json", "w") as fout:
    json.dump(loosely_typed_names_map, fout)


for mongo_deposit_exchange in get_deposit_exchanges():
    mongo_from = mongo_deposit_exchange["from"]
    mongo_to = mongo_deposit_exchange["to"]
    mongo_date = mongo_deposit_exchange["date"]
    mongo_amount = mongo_deposit_exchange["amount"]
    mongo_initiator = mongo_deposit_exchange["initiator"]

    postgres_from_user = get_user(mongo_from, db=db)
    postgres_to_user = get_user(mongo_to, db=db)

    postgres_deposit_exchange = models.DepositExchange(
        fromUserId=postgres_from_user.id if postgres_from_user is not None else None,
        toUserId=postgres_to_user.id if postgres_to_user is not None else None,
        date=mongo_date,
        amount=mongo_amount
    )

    db.add(postgres_deposit_exchange)
    db.commit()

# TODO: workshop days
