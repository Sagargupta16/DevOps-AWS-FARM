"""Load demo users and blog posts through the public API.

    python scripts/seed.py                         # against http://localhost:8000
    python scripts/seed.py --url http://localhost:3000

Safe to re-run: a user whose email already exists comes back as 409 and is skipped,
and blog posts are only added when no post with the same title is there yet.
Standard library only, so it runs from any Python 3.11+ without the app's dependencies.
Demo data only goes to a local app: --url must be http(s) on localhost, 127.0.0.1 or ::1.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")

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


def local_base_url(url: str) -> str:
    """Rebuild the base URL from an allowlisted scheme and host, or raise ValueError."""
    parts = urllib.parse.urlsplit(url)
    scheme = {"http": "http", "https": "https"}.get(parts.scheme)
    host = next((h for h in LOCAL_HOSTS if h == parts.hostname), None)
    if scheme is None or host is None:
        raise ValueError(
            f"--url must be http(s) on {', '.join(LOCAL_HOSTS)}, got {url!r}"
        )
    netloc = f"[{host}]" if ":" in host else host
    if parts.port is not None:
        netloc += f":{int(parts.port)}"
    return f"{scheme}://{netloc}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    try:
        base_url = local_base_url(parser.parse_args().url)
    except ValueError as e:
        parser.error(str(e))
    sys.exit(seed(base_url))
