import yaml
import pymongo

with open("config/secrets.yml", "r") as stream:
    secrets = yaml.safe_load(stream)

mongodb_host = secrets["mongodb"]["host"]
mongodb_port = secrets["mongodb"]["port"]
mongodb_username = secrets["mongodb"]["username"]
mongodb_password = secrets["mongodb"]["password"]
mongodb_database = secrets["mongodb"]["database"]


def get_database():
    client = pymongo.MongoClient(mongodb_database)
    return client["blogging"]


def get_blogs_collection():
    db = get_database()
    return db["blogs"]


def get_users_collection():
    db = get_database()
    return db["users"]
