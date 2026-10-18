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
- **Deploy target**: AWS ECS (image in ECR) via manual `deploy.yml` / `main.yml`, both in demo mode behind the `DEPLOY_ENABLED` repo variable

## Run

```
pip install -r requirements.txt
cd client && npm install && npm run build   # produces ../client_build
uvicorn main:app --reload --port 8000
```

Or all-in-one: `docker compose up --build` (starts a `mongo:8.2` service, runs the tests container against it, starts the app on port 8000 only if tests pass).

Frontend dev server: `cd client && npm run dev` (port 3000; Vite proxies `/user` and `/blog` to localhost:8000, the client always calls same-origin).

## Test

```
pytest                                    # plain run
pytest tests/ --cov=. --cov-fail-under=80 # what CI enforces
```

## Entry points

- `main.py` -- FastAPI app; includes blog/user routers, mounts `client_build/` as static frontend at `/`
- `client/src/` -- React frontend source (Vite)

## Key files

- `routes/` -> `services/` -> `models/` -- API layering (blog + user in each)
- `config/secrets_parser.py` -- resolves the Mongo connection (`MONGODB_URL` env var first, else `config/secrets.yml`)
- `config/secrets.yml.example` -- template; copy to `config/secrets.yml` for Atlas credentials
- `.github/workflows/ci.yml` -- every push/PR: flake8, pytest against a Mongo service container (80% gate), Vite build
- `.github/workflows/deploy.yml` -- manual: test (Mongo service container) -> build -> ECR push -> ECS deploy

## Gotchas

- `uvicorn main:app` crashes at import if `client_build/` is missing -- build the client first. `npm run build` in `client/` writes straight to `../client_build` (Vite `outDir`).
- Mongo connection resolves in order: `MONGODB_URL` env var -> `config/secrets.yml` (gitignored) -> `mongodb://localhost:27017/blogging` fallback. The parser warns on a missing secrets file but never fails.
- `ci.yml` hard-gates on 80% pytest coverage; the manual AWS pipelines run their tests with `continue-on-error`.
- `ci.yml` installs `requirements.lock.txt` (hash-locked, generated) with `--require-hashes --only-binary :all:`, not `requirements.txt`. After editing `requirements.txt`, regenerate the lock with the `uv pip compile` command in its header or CI installs stale pins.
- bcrypt is called directly (passlib was dropped: unmaintained, raises on bcrypt 5). bcrypt rejects passwords over 72 bytes, so `UserIn` validates that and returns 422.
- `config/secrets.yml` is in `.dockerignore`; containers get the connection from `MONGODB_URL`.
- Local `.env` and `config/secrets.yml` exist on disk but are gitignored and untracked -- keep it that way.

## Repo-specific rules

- Uses pip + requirements.txt and npm (not uv/pnpm) -- predates the workspace defaults; keep as-is unless migrating deliberately.

## API routes

- `/user`, `/user/{user_id}` -- user CRUD (passwords bcrypt-hashed); no login/token endpoint
- `/blog`, `/blog/{blog_id}` -- blog post CRUD
- OpenAPI at `/docs` when the server is running.
