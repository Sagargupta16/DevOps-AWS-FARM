"""
Load demo users and blog posts through the public API.

    python scripts/seed.py                         # against http://localhost:8000
    python scripts/seed.py --url http://localhost:3000

Safe to re-run: a user whose email already exists comes back as 409 and is skipped,
and blog posts are only added when no post with the same title is there yet.
Standard library only, so it runs from any Python 3.11+ without the app's dependencies.
Demo data only goes to a local app: --url must be http(s) on localhost, 127.0.0.1 or ::1.
Demo passwords are random per run; the app has no login, so nothing needs them later.
"""

import argparse
import http.client
import json
import secrets
import sys
import urllib.parse

LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")

USERS = [
    {"name": "Asha Rao", "email": "asha@example.com"},
    {"name": "Dev Malhotra", "email": "dev@example.com"},
    {"name": "Meera Iyer", "email": "meera@example.com"},
]

BLOGS = [
    {
        "title": "Why our CI went green while user signup was broken",
        "content": "continue-on-error on the test step hid a bcrypt 5 and passlib crash for six weeks. "
        "The fix: a blocking pytest job against a real MongoDB service container.",
        "creator": "Asha Rao",
    },
    {
        "title": "Keyless deploys to ECS with GitHub OIDC",
        "content": "The workflow trades a short-lived OIDC token for an IAM role scoped to one environment. "
        "No access keys live in the repo settings.",
        "creator": "Dev Malhotra",
    },
    {
        "title": "One image for the API and the React app",
        "content": "A multi-stage Dockerfile builds the Vite client, then serves it from FastAPI. "
        "Same origin everywhere, so there is no CORS to configure.",
        "creator": "Meera Iyer",
    },
]


class LocalApi:
    """JSON client for an app on a loopback host, built from an allowlisted scheme and host."""

    def __init__(self, url: str):
        parts = urllib.parse.urlsplit(url)
        connection = {
            "http": http.client.HTTPConnection,
            "https": http.client.HTTPSConnection,
        }.get(parts.scheme)
        host = next((h for h in LOCAL_HOSTS if h == parts.hostname), None)
        if connection is None or host is None:
            raise ValueError(
                f"--url must be http(s) on {', '.join(LOCAL_HOSTS)}, got {url!r}"
            )
        self.connection = connection
        self.host = host
        self.port = parts.port
        netloc = f"[{host}]" if ":" in host else host
        if self.port is not None:
            netloc += f":{self.port}"
        self.base = f"{parts.scheme}://{netloc}"

    def request(
        self, method: str, path: str, body: dict | None = None
    ) -> tuple[int, object]:
        conn = self.connection(self.host, self.port, timeout=10)
        try:
            conn.request(
                method,
                path,
                body=json.dumps(body) if body is not None else None,
                headers={"Content-Type": "application/json"},
            )
            resp = conn.getresponse()
            return resp.status, json.loads(resp.read() or b"null")
        finally:
            conn.close()


def seed(api: LocalApi) -> int:
    try:
        status, health = api.request("GET", "/health")
    except OSError as e:
        print(f"Cannot reach the API at {api.base}: {e}", file=sys.stderr)
        return 1
    if status != 200:
        print(
            f"API not healthy at {api.base}/health: {status} {health}", file=sys.stderr
        )
        return 1

    for user in USERS:
        status, _ = api.request(
            "POST", "/user", user | {"password": secrets.token_urlsafe(12)}
        )
        outcome = {201: "created", 409: "exists, skipped"}.get(
            status, f"failed ({status})"
        )
        print(f"user {user['email']}: {outcome}")

    _, existing = api.request("GET", "/blog")
    titles = {b["title"] for b in existing or []}
    for blog in BLOGS:
        if blog["title"] in titles:
            print(f"blog '{blog['title']}': exists, skipped")
            continue
        status, _ = api.request("POST", "/blog", blog)
        print(
            f"blog '{blog['title']}': {'created' if status == 201 else f'failed ({status})'}"
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    try:
        local_api = LocalApi(parser.parse_args().url)
    except ValueError as e:
        parser.error(str(e))
    sys.exit(seed(local_api))
