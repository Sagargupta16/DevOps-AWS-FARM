"""Email is unique per user (409 Conflict); blog titles are not unique."""

import pytest
from fastapi import HTTPException, status

from models.user_models import UserIn
from services.user_services import DUPLICATE_EMAIL, create_user


def test_duplicate_email_returns_409(client, new_user):
    payload = new_user()
    assert client.post("/user", json=payload).status_code == 201

    again = client.post("/user", json=new_user(email=payload["email"]))
    assert again.status_code == 409
    assert again.json() == {"detail": DUPLICATE_EMAIL}


def test_update_to_taken_email_returns_409(client, new_user):
    taken = new_user()
    client.post("/user", json=taken)
    other_id = client.post("/user", json=new_user()).json()["id"]

    clash = client.put(f"/user/{other_id}", json=new_user(email=taken["email"]))
    assert clash.status_code == 409


def test_unique_index_catches_a_race(client, new_user, monkeypatch):
    # Two requests that both pass the read check: the unique index makes the second insert fail
    payload = new_user()
    client.post("/user", json=payload)
    monkeypatch.setattr(
        "services.user_services._reject_taken_email", lambda *a, **k: None
    )

    with pytest.raises(HTTPException) as exc:
        create_user(UserIn(**new_user(email=payload["email"])))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


def test_blogs_with_same_title_are_allowed(client, new_blog):
    first = client.post("/blog", json=new_blog(title="Same title"))
    second = client.post("/blog", json=new_blog(title="Same title"))
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
