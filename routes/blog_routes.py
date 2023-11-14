from fastapi import APIRouter, status
from typing import List
from models.blog_models import BlogIn, BlogOut
from services.blog_services import (
    create_blog,
    get_blogs,
    get_blog,
    delete_blog,
    update_blog,
)

router = APIRouter()


@router.post("/blog", status_code=status.HTTP_201_CREATED, tags=["blogs"])
def create_blog_route(blog: BlogIn):
    return create_blog(blog)


@router.get(
    "/blog",
    response_model=List[BlogOut],
    status_code=status.HTTP_200_OK,
    tags=["blogs"],
)
def get_blogs_route():
    return get_blogs()


@router.get(
    "/blog/{blog_id}",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    tags=["blogs"],
)
def get_blog_route(blog_id: str):
    return get_blog(blog_id)


@router.delete(
    "/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["blogs"]
)
def delete_blog_route(blog_id: str):
    return delete_blog(blog_id)


@router.put(
    "/blog/{blog_id}",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    tags=["blogs"],
)
def update_blog_route(blog_id: str, blog: BlogIn):
    return update_blog(blog_id, blog)
