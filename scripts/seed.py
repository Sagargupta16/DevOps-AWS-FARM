"""Load demo users and blog posts through the public API.

    python scripts/seed.py                         # against http://localhost:8000
    python scripts/seed.py --url http://localhost:3000

Safe to re-run: a user whose email already exists comes back as 409 and is skipped,
and blog posts are only added when no post with the same title is there yet.
Standard library only, so it runs from any Python 3.11+ without the app's dependencies.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

USERS = [
    {"name": "Asha Rao", "email": "asha@example.com", "password": "demo-pass-1"},
    {"name": "Dev Malhotra", "email": "dev@example.com", "password": "demo-pass-2"},
    {"name": "Meera Iyer", "email": "meera@example.com", "password": "demo-pass-3"},
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


def request(method: str, url: str, body: dict | None = None) -> tuple[int, object]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def seed(base: str) -> int:
    try:
        status, health = request("GET", f"{base}/health")
    except urllib.error.URLError as e:
        print(f"Cannot reach the API at {base}: {e.reason}", file=sys.stderr)
        return 1
    if status != 200:
        print(f"API not healthy at {base}/health: {status} {health}", file=sys.stderr)
        return 1

    for user in USERS:
        status, _ = request("POST", f"{base}/user", user)
        outcome = {201: "created", 409: "exists, skipped"}.get(
            status, f"failed ({status})"
        )
        print(f"user {user['email']}: {outcome}")

    _, existing = request("GET", f"{base}/blog")
    titles = {b["title"] for b in existing or []}
    for blog in BLOGS:
        if blog["title"] in titles:
            print(f"blog '{blog['title']}': exists, skipped")
            continue
        status, _ = request("POST", f"{base}/blog", blog)
        print(
            f"blog '{blog['title']}': {'created' if status == 201 else f'failed ({status})'}"
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    sys.exit(seed(parser.parse_args().url.rstrip("/")))
