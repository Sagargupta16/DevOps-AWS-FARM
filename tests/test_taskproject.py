"""Happy-path CRUD for users and blogs, exercised over HTTP through the real app."""

import bcrypt

from config.secrets_parser import get_users_collection


def test_create_and_get_user(client, new_user):
    payload = new_user()
    created = client.post("/user", json=payload)
    assert created.status_code == 201
    user_id = created.json()["id"]

    fetched = client.get(f"/user/{user_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body == {"id": user_id, "name": payload["name"], "email": payload["email"]}
    assert "password" not in body


def test_password_is_stored_as_bcrypt_hash(client, new_user):
    payload = new_user()
    user_id = client.post("/user", json=payload).json()["id"]

    stored = get_users_collection().find_one({"id": user_id})
    assert stored["password"] != payload["password"]
    assert bcrypt.checkpw(payload["password"].encode(), stored["password"].encode())


def test_list_users_includes_created(client, new_user):
    ids = {client.post("/user", json=new_user()).json()["id"] for _ in range(2)}

    listed = client.get("/user")
    assert listed.status_code == 200
    assert ids <= {u["id"] for u in listed.json()}


def test_update_user_rehashes_password(client, new_user):
    user_id = client.post("/user", json=new_user()).json()["id"]
    changes = new_user(password="a-new-password")

    updated = client.put(f"/user/{user_id}", json=changes)
    assert updated.status_code == 200

    fetched = client.get(f"/user/{user_id}").json()
    assert fetched["name"] == changes["name"]
    assert fetched["email"] == changes["email"]
    stored = get_users_collection().find_one({"id": user_id})
    assert bcrypt.checkpw(b"a-new-password", stored["password"].encode())


def test_user_can_keep_own_email_on_update(client, new_user):
    payload = new_user()
    user_id = client.post("/user", json=payload).json()["id"]

    updated = client.put(
        f"/user/{user_id}", json=new_user(name=payload["name"], email=payload["email"])
    )
    assert updated.status_code == 200


def test_delete_user(client, new_user):
    user_id = client.post("/user", json=new_user()).json()["id"]

    deleted = client.delete(f"/user/{user_id}")
    assert deleted.status_code == 202
    assert client.get(f"/user/{user_id}").status_code == 404


def test_blog_crud(client, new_blog):
    payload = new_blog()
    created = client.post("/blog", json=payload)
    assert created.status_code == 201
    blog_id = created.json()["id"]

    fetched = client.get(f"/blog/{blog_id}")
    assert fetched.status_code == 200
    assert fetched.json() == {"id": blog_id, **payload}

    assert blog_id in {b["id"] for b in client.get("/blog").json()}

    changes = new_blog(title="Edited title")
    updated = client.put(f"/blog/{blog_id}", json=changes)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Edited title"

    assert client.delete(f"/blog/{blog_id}").status_code == 204
    assert client.get(f"/blog/{blog_id}").status_code == 404
