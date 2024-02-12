from pymongo import MongoClient
from app.mongodb_config import mongodb_user, mongodb_pwd, mongodb_host, mongodb_port

client = MongoClient(f"mongodb://{mongodb_user}:{mongodb_pwd}@{mongodb_host}:{mongodb_port}")
db = client["becycleDB"]


def deref(ref):
    return db.dereference(ref)


# read users
def get_users():
    users_collection = db["users"]
    return [user for user in users_collection.find()]


def get_bikes():
    bikes_collection = db["bikes"]
    return [bike for bike in bikes_collection.find()]


def get_persons():
    persons_collection = db["persons"]
    return [person for person in persons_collection.find()]


def get_appointment_types():
    appointment_types_collection = db["appointmentTypes"]
    return [appointment_type for appointment_type in appointment_types_collection.find()]


def get_appointments():
    appointments_collection = db["appointments"]
    return [appointment for appointment in appointments_collection.find()]


# read contracts
def get_contracts():
    contracts_collection = db["contracts"]
    return [contract for contract in contracts_collection.find()]


# read deposit exchanges
def get_deposit_exchanges():
    deposit_exchanges_collection = db["depositExchanges"]
    return [deposit_exchange for deposit_exchange in deposit_exchanges_collection.find()]


def get_workshop_days():
    workshop_days_collection = db["workshopdays"]
    return [workshop_day for workshop_day in workshop_days_collection.find()]


def get_appointment_general():
    appointment_general_collection = db["appointmentGeneral"]
    return [appointment_general for appointment_general in appointment_general_collection.find()]


def get_appointment_concurrency():
    appointment_concurrency_collection = db["appointmentConcurrency"]
    return [appointment_concurrency for appointment_concurrency in appointment_concurrency_collection.find()]
