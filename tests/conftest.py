import uuid

import pytest
from fastapi.testclient import TestClient

from main import app
from config.secrets_parser import get_blogs_collection, get_users_collection

# Every test document carries this marker so cleanup never touches real data in a shared database
MARKER = "pytest-" + uuid.uuid4().hex[:8]


@pytest.fixture(scope="session")
def client():
    # The context manager runs the lifespan, which creates the unique email index
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True, scope="session")
def cleanup():
    yield
    get_users_collection().delete_many({"name": {"$regex": f"^{MARKER}"}})
    get_blogs_collection().delete_many({"creator": {"$regex": f"^{MARKER}"}})


@pytest.fixture
def new_user():
    """Payload for a user with a unique name and email."""

    def make(**overrides):
        tag = uuid.uuid4().hex[:8]
        payload = {
            "name": f"{MARKER}-{tag}",
            "email": f"{MARKER}-{tag}@example.com",
            "password": "s3cret-pass",
        }
        return payload | overrides

    return make


@pytest.fixture
def new_blog():
    """Payload for a blog post whose creator carries the cleanup marker."""

    def make(**overrides):
        tag = uuid.uuid4().hex[:8]
        payload = {
            "title": f"Post {tag}",
            "content": "Shipping FastAPI to ECS",
            "creator": f"{MARKER}-{tag}",
        }
        return payload | overrides

    return make
