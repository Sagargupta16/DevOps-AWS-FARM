import yaml
import pymongo
import os

# Try to get MongoDB URL from environment variable first, fallback to secrets file
mongodb_url = os.getenv('MONGODB_URL')

if not mongodb_url:
    # Fallback to secrets file if environment variable is not set
    try:
        with open("config/secrets.yml", "r") as stream:
            secrets = yaml.safe_load(stream)
        
        mongodb_host = secrets["mongodb"]["host"]
        mongodb_port = secrets["mongodb"]["port"]
        mongodb_username = secrets["mongodb"]["username"]
        mongodb_password = secrets["mongodb"]["password"]
        mongodb_database = secrets["mongodb"]["database"]
        
        # Use the database field as the full connection string if it starts with mongodb://
        if mongodb_database.startswith('mongodb://') or mongodb_database.startswith('mongodb+srv://'):
            mongodb_url = mongodb_database
        else:
            mongodb_url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}"
    except Exception as e:
        print(f"Warning: Could not read secrets file: {e}")
        print("Using default local MongoDB connection for testing/development")
        # Default local MongoDB connection for CI/testing
        mongodb_url = "mongodb://localhost:27017/blogging"

print(f"MongoDB connection configured: {mongodb_url.replace(mongodb_url.split('@')[0].split('://')[1] + '@', '***:***@') if '@' in mongodb_url else mongodb_url}")


def get_database():
    client = pymongo.MongoClient(mongodb_url)
    return client["blogging"]


def get_blogs_collection():
    db = get_database()
    return db["blogs"]


def get_users_collection():
    db = get_database()
    return db["users"]
