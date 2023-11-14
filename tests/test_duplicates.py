from fastapi import HTTPException, status
from routes.blog_routes import create_blog_route, delete_blog_route
from routes.user_routes import create_user_route, delete_user_route
from models.blog_models import BlogIn
from models.user_models import UserIn


def test_create_duplicate_user():
    user = UserIn(name="test", email="test@gmail.com", password="test123")
    try:
        created_user = create_user_route(user)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == "User with the same email already exists"
    finally:
        delete_user_route(created_user["id"])


def test_create_duplicate_blog():
    blog = BlogIn(title="test", content="test", creator="test")
    try:
        created_blog = create_blog_route(blog)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == "Blog with the same title already exists"
    finally:
        delete_blog_route(created_blog["id"])
