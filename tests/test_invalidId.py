"""Malformed ids and bodies: 404 for ids that match nothing, 422 for bodies that fail validation."""

import pytest
from fastapi import HTTPException, status

from models.user_models import BCRYPT_MAX_BYTES
from services.blog_services import get_blog
from services.user_services import get_user


@pytest.mark.parametrize("lookup", [get_user, get_blog])
def test_service_raises_404_for_invalid_id(lookup):
    with pytest.raises(HTTPException) as exc:
        lookup("not-an-id")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("resource", ["user", "blog"])
def test_invalid_id_over_http(client, resource):
    assert client.get(f"/{resource}/not-an-id").status_code == 404


def test_password_over_bcrypt_limit_returns_422(client, new_user):
    too_long = "x" * (BCRYPT_MAX_BYTES + 1)
    response = client.post("/user", json=new_user(password=too_long))
    assert response.status_code == 422
    assert "at most 72 bytes" in response.text


def test_password_limit_counts_bytes_not_characters(client, new_user):
    # 24 three-byte characters are 72 bytes: allowed. One more character crosses the limit
    assert client.post("/user", json=new_user(password="€" * 24)).status_code == 201
    assert client.post("/user", json=new_user(password="€" * 25)).status_code == 422


@pytest.mark.parametrize("missing", ["name", "email", "password"])
def test_user_missing_field_returns_422(client, new_user, missing):
    payload = new_user()
    del payload[missing]
    assert client.post("/user", json=payload).status_code == 422


def test_blog_missing_field_returns_422(client):
    assert client.post("/blog", json={"title": "only a title"}).status_code == 422
