from fastapi import HTTPException, status
from routes.blog_routes import get_blog_route, update_blog_route, delete_blog_route
from routes.user_routes import get_user_route, update_user_route, delete_user_route
from models.blog_models import BlogIn
from models.user_models import UserIn


def test_user_not_found():
    try:
        get_user_route("non_existing_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_blog_not_found():
    try:
        get_blog_route("non_existing_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_not_found():
    try:
        update_user_route(
            "non_existing_id",
            UserIn(name="test", email="test@gmail.com", password="test123"),
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_update_blog_not_found():
    try:
        update_blog_route(
            "non_existing_id", BlogIn(title="test", content="test", creator="test")
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_not_found():
    try:
        delete_user_route("non_existing_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_delete_blog_not_found():
    try:
        delete_blog_route("non_existing_id")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
