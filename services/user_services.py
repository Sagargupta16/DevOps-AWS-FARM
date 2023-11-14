from fastapi import Depends, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from models.user_models import UserIn
from config.secrets_parser import get_users_collection, get_database
from config.logging import logger
from utils.hashing import Hash

users_collection = get_users_collection()


def create_user(user: UserIn, db: MongoClient = Depends(get_database)):
    logger.info("Creating user")
    user = user.dict()
    user["id"] = str(ObjectId())
    user["password"] = Hash.bcrypt(user["password"])
    users_collection.insert_one(user)
    return {
        "message": "User created successfully",
        "id": user["id"],
    }


def get_users(db: MongoClient = Depends(get_database)):
    logger.info("Getting All users")
    users = users_collection.find()
    users = list(users)
    if users:
        return users
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


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
    user = user.dict()
    user["password"] = Hash.bcrypt(user["password"])
    user = users_collection.find_one_and_update(
        {"id": user_id}, {"$set": user}, return_document=True
    )
    if user:
        return user["id"]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
