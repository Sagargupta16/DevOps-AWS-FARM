import pymongo
from fastapi import Depends, HTTPException, status
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from models.user_models import UserIn
from config.secrets_parser import get_users_collection, get_database
from config.logging import logger
from utils.hashing import Hash

users_collection = get_users_collection()

DUPLICATE_EMAIL = "User with the same email already exists"


def ensure_indexes():
    # Backs the duplicate check below so two concurrent creates cannot both win.
    # Bounded so a down database delays startup by seconds, not the 30s selection timeout
    with pymongo.timeout(5):
        users_collection.create_index("email", unique=True)


def _reject_taken_email(email: str, user_id: str | None = None):
    query = {"email": email}
    if user_id:
        query["id"] = {"$ne": user_id}
    if users_collection.find_one(query, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DUPLICATE_EMAIL)


def create_user(user: UserIn, db: MongoClient = Depends(get_database)):
    logger.info("Creating user")
    _reject_taken_email(user.email)
    user = user.model_dump()
    user["id"] = str(ObjectId())
    user["password"] = Hash.bcrypt(user["password"])
    try:
        users_collection.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DUPLICATE_EMAIL)
    return {
        "message": "User created successfully",
        "id": user["id"],
    }


def get_users(db: MongoClient = Depends(get_database)):
    logger.info("Getting All users")
    users = users_collection.find()
    return list(users)


def get_user(user_id: str, db: MongoClient = Depends(get_database)):
    logger.info("Getting user")
    user = users_collection.find_one({"id": user_id})
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def delete_user(user_id: str, db: MongoClient = Depends(get_database)):
    logger.info("Deleting user")
    user = users_collection.find_one({"id": user_id})
    if user:
        users_collection.delete_one({"id": user_id})
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def update_user(user_id: str, user: UserIn, db: MongoClient = Depends(get_database)):
    logger.info("Updating user")
    _reject_taken_email(user.email, user_id)
    user = user.model_dump()
    user["password"] = Hash.bcrypt(user["password"])
    try:
        user = users_collection.find_one_and_update(
            {"id": user_id}, {"$set": user}, return_document=True
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DUPLICATE_EMAIL)
    if user:
        return user["id"]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
