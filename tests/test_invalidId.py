from fastapi import HTTPException, status
from routes.blog_routes import update_blog_route, delete_blog_route
from routes.user_routes import update_user_route, delete_user_route
from models.blog_models import BlogIn
from models.user_models import UserIn


def test_update_user_invalid_id():
    try:
        update_user_route(
            "invalid_id",
            UserIn(name="test", email="test@gmail.com", password="test123"),
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_update_blog_invalid_id():
    try:
        update_blog_route(
            "invalid_id", BlogIn(title="test", content="test", creator="test")
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_invalid_id():
    try:
        delete_user_route("invalid_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_delete_blog_invalid_id():
    try:
        delete_blog_route("invalid_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
