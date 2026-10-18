import yaml
import pymongo
import os
from functools import cache

# Try to get MongoDB URL from environment variable first, fallback to secrets file
mongodb_url = os.getenv("MONGODB_URL")
config_source = "MONGODB_URL environment variable"

if not mongodb_url:
    # Fallback to secrets file if environment variable is not set
    config_source = "config/secrets.yml"
    try:
        with open("config/secrets.yml", "r") as stream:
            secrets = yaml.safe_load(stream)

        mongodb_host = secrets["mongodb"]["host"]
        mongodb_port = secrets["mongodb"]["port"]
        mongodb_username = secrets["mongodb"]["username"]
        mongodb_password = secrets["mongodb"]["password"]
        mongodb_database = secrets["mongodb"]["database"]

        # Use the database field as the full connection string if it starts with mongodb://
        if mongodb_database.startswith("mongodb://") or mongodb_database.startswith(
            "mongodb+srv://"
        ):
            mongodb_url = mongodb_database
        else:
            mongodb_url = (
                f"mongodb://{mongodb_username}:{mongodb_password}"
                f"@{mongodb_host}:{mongodb_port}/{mongodb_database}"
            )
    except Exception as e:
        print(f"Warning: Could not read secrets file: {e}")
        print("Using default local MongoDB connection for testing/development")
        # Default local MongoDB connection for CI/testing
        mongodb_url = "mongodb://localhost:27017/blogging"
        config_source = "default local connection"

# Log where the URL came from, never any part of it: it can carry credentials
print(f"MongoDB connection configured from {config_source}")


@cache
def get_client():
    # One client per process: MongoClient owns a connection pool and is thread-safe
    return pymongo.MongoClient(mongodb_url)


def get_database():
    return get_client()["blogging"]


def ping_database(timeout_seconds: float = 2.0) -> None:
    """Raise if MongoDB does not answer a ping within timeout_seconds."""
    with pymongo.timeout(timeout_seconds):
        get_client().admin.command("ping")


def get_blogs_collection():
    db = get_database()
    return db["blogs"]


def get_users_collection():
    db = get_database()
    return db["users"]
