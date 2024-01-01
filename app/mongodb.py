from pymongo import MongoClient
from mongodb_config import mongodb_user, mongodb_pwd, mongodb_host, mongodb_port

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





# read persons


# read bikes


# read appointments


# read workshop days







