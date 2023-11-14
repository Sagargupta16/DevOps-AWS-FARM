from fastapi import Depends, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from models.blog_models import BlogIn
from config.secrets_parser import get_blogs_collection, get_database
from config.logging import logger

blogs_collection = get_blogs_collection()


def create_blog(blog: BlogIn, db: MongoClient = Depends(get_database)):
    logger.info("Creating blog")
    blog = blog.dict()
    blog["id"] = str(ObjectId())
    blogs_collection.insert_one(blog)
    return {
        "message": "Blog created successfully",
        "id": blog["id"],
    }


def get_blogs(db: MongoClient = Depends(get_database)):
    logger.info("Getting All blogs")
    blogs = blogs_collection.find()
    blogs = list(blogs)
    if blogs:
        return blogs
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def get_blog(blog_id: str, db: MongoClient = Depends(get_database)):
    logger.info("Getting blog")
    blog = blogs_collection.find_one({"id": blog_id})
    if blog:
        return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def delete_blog(blog_id: str, db: MongoClient = Depends(get_database)):
    logger.info("Deleting blog")
    blog = blogs_collection.find_one({"id": blog_id})
    if blog:
        blogs_collection.delete_one({"id": blog_id})
        return {"message": "Blog deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def update_blog(blog_id: str, blog: BlogIn, db: MongoClient = Depends(get_database)):
    logger.info("Updating blog")
    blog = blog.dict()
    blog = blogs_collection.find_one_and_update(
        {"id": blog_id}, {"$set": blog}, return_document=True
    )
    if blog:
        return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
