# CLAUDE.md

> This file stacks on top of the workspace root at `C:\Code\GitHub\`:
> - Root [`CLAUDE.md`](../../CLAUDE.md) -- voice, rules, routing map, references, skills, slash commands, conventions.
> - Root [`MEMORY.md`](../../MEMORY.md) -- live facts across repos.
> - Root [`STATUS.md`](../../STATUS.md) -- live PR/CI/security dashboard.
> - [`.claude/resources/`](../../.claude/resources/README.md) -- deep reference for collaboration, workflow, git, OSS, debugging, voice.
>
> Read those first. The guidance below only adds **repo-specific context** -- it does not override anything in the root.

## Project

FARM-stack (FastAPI + React + MongoDB) demo app with user and blog CRUD, built to showcase a DevOps pipeline: Docker image -> ECR -> ECS via GitHub Actions.

## Stack

- **Language**: Python 3.11+ (backend), JavaScript (frontend)
- **Framework**: FastAPI + Uvicorn; React 19 built with Vite 8
- **Database**: MongoDB Atlas (PyMongo)
- **Package manager**: pip (`requirements.txt`), npm (`client/package.json`)
- **Deploy target**: AWS ECS (image in ECR) via manual `deploy.yml` / `main.yml`, both in demo mode behind the `DEPLOY_ENABLED` repo variable. `deploy.yml` has live steps (GitHub OIDC, no AWS keys); `main.yml` keeps its AWS steps commented

## Run

```
pip install -r requirements.txt
cd client
npm install
npm run build            # produces ../client_build
cd ..
uvicorn main:app --reload --port 8000
python scripts/seed.py   # demo users and posts (idempotent)
```

Or all-in-one: `docker compose up --build` (starts a `mongo:8.2` service, runs the tests container against it, starts the app on port 8000 only if tests pass).

Frontend dev server: `npm run dev` from `client/` (port 3000; Vite proxies `/user`, `/blog` and `/health` to localhost:8000, the client always calls same-origin).

README screenshots: `npm run screenshots` from `client/` against a running, seeded app (`BASE_URL` overrides `http://localhost:8000`); writes `assets/screenshots/*.png`.

README diagrams: orrery specs in `assets/diagrams/*.yaml`, each with its render command in the header (`-f svg --theme both` writes the `-light` and `-dark` SVGs). Change a workflow, `aws/` or the app layering and the matching spec changes with it; `orrery verify <spec>` fails when an `evidence:` line has moved.

## Test

```
pytest                                    # plain run
pytest tests/ --cov=. --cov-fail-under=80 # what CI enforces
```

## Entry points

- `main.py` -- FastAPI app; lifespan creates the unique email index, JSON request-log middleware, includes health/blog/user routers, mounts `client_build/` at `/` when it exists
- `client/src/` -- React frontend source (Vite)

## Key files

- `routes/` -> `services/` -> `models/` -- API layering (blog + user in each)
- `config/secrets_parser.py` -- resolves the Mongo connection (`MONGODB_URL` env var first, else `config/secrets.yml`)
- `config/secrets.yml.example` -- template; copy to `config/secrets.yml` for Atlas credentials
- `.github/workflows/ci.yml` -- every push/PR: flake8, pytest against a Mongo service container (80% gate), Vite build
- `.github/workflows/deploy.yml` -- manual: blocking test (Mongo service container) -> OIDC -> build -> ECR push (SHA tag) -> render task def from family -> ECS deploy -> `/health` smoke test
- `aws/` -- OIDC trust policy, deploy role policy, task definition template, setup and teardown guide (`/docs/` is gitignored, so these live at the root)
- `routes/health_routes.py` -- `GET /health`, 200 when MongoDB answers a 2s ping, else 503

## Gotchas

- Without `client_build/` the app serves the API only and logs a warning (`/` is 404). `npm run build` in `client/` writes straight to `../client_build` (Vite `outDir`).
- `get_client()` in `config/secrets_parser.py` is cached: one `MongoClient` per process. The database name is always `blogging`, whatever path `MONGODB_URL` carries.
- `LOG_FORMAT=json` (set in the Dockerfile) switches to `config/json_formatter.py`; `extra=` fields become JSON keys.
- Tests drive the app through `TestClient` (needs `httpx`, which starlette now warns should become `httpx2`). Test docs carry a per-run `pytest-xxxx` marker in name/creator and only those are cleaned up -- keep new tests on the `new_user`/`new_blog` fixtures.
- Mongo connection resolves in order: `MONGODB_URL` env var -> `config/secrets.yml` (gitignored) -> `mongodb://localhost:27017/blogging` fallback. The parser warns on a missing secrets file but never fails.
- `ci.yml` and `deploy.yml` hard-gate on 80% pytest coverage; `main.yml` runs its tests with `continue-on-error`.
- `ci.yml`, `deploy.yml`, `main.yml` and both Dockerfiles install `requirements.lock.txt` (hash-locked, generated) with `--require-hashes --only-binary :all:`, not `requirements.txt`. After editing `requirements.txt`, regenerate the lock with the `uv pip compile` command in its header or CI and the images install stale pins.
- Images are `python:3.14-slim`, not alpine: pymongo has no musllinux wheel, so wheels-only installs fail on alpine.
- bcrypt is called directly (passlib was dropped: unmaintained, raises on bcrypt 5). bcrypt rejects passwords over 72 bytes, so `UserIn` validates that and returns 422.
- `config/secrets.yml` is in `.dockerignore`; containers get the connection from `MONGODB_URL`.
- Local `.env` and `config/secrets.yml` exist on disk but are gitignored and untracked -- keep it that way.

## Repo-specific rules

- Uses pip + requirements.txt and npm (not uv/pnpm) -- predates the workspace defaults; keep as-is unless migrating deliberately.

## API routes

- `/health` -- MongoDB ping, 200 or 503
- `/user`, `/user/{user_id}` -- user CRUD (passwords bcrypt-hashed, email unique: 409 on clash); no login/token endpoint
- `/blog`, `/blog/{blog_id}` -- blog post CRUD
- OpenAPI at `/docs` when the server is running.
