from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.dbref import DBRef
from mongodb_config import mongodb_user, mongodb_pwd, mongodb_host, mongodb_port

client = MongoClient(f"mongodb://{mongodb_user}:{mongodb_pwd}@{mongodb_host}:{mongodb_port}")
db = client["becycleDB"]


# read contracts


# read deposit exchanges


# read users


# read persons


# read bikes


# read appointments


# read workshop days







