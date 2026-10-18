"""Unknown ids return 404 on every read, update and delete route."""

import pytest

MISSING_ID = "000000000000000000000000"


@pytest.mark.parametrize("resource", ["user", "blog"])
def test_get_missing_returns_404(client, resource):
    assert client.get(f"/{resource}/{MISSING_ID}").status_code == 404


@pytest.mark.parametrize("resource", ["user", "blog"])
def test_delete_missing_returns_404(client, resource):
    assert client.delete(f"/{resource}/{MISSING_ID}").status_code == 404


def test_update_missing_user_returns_404(client, new_user):
    assert client.put(f"/user/{MISSING_ID}", json=new_user()).status_code == 404


def test_update_missing_blog_returns_404(client, new_blog):
    assert client.put(f"/blog/{MISSING_ID}", json=new_blog()).status_code == 404
