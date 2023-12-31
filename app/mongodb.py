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


# read contracts
def get_contracts():
    contracts_collection = db["contracts"]
    return [contract for contract in contracts_collection.find()]


# read deposit exchanges





# read persons


# read bikes


# read appointments


# read workshop days







